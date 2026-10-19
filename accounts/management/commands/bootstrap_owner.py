import getpass
from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from portal.models import AuditLog


class Command(BaseCommand):
    help = 'Securely initializes the primary Business Owner account for Z&D ELECTRONIC DEALS'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Owner email address')
        parser.add_argument('--first-name', type=str, help='Owner first name')
        parser.add_argument('--last-name', type=str, help='Owner last name')
        parser.add_argument('--password', type=str, help='Secure owner password')

    def handle(self, *args, **options):
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        password = options.get('password')

        if not email:
            email = input("Enter Owner Email Address: ").strip().lower()
        if not first_name:
            first_name = input("Enter Owner First Name: ").strip()
        if not last_name:
            last_name = input("Enter Owner Last Name: ").strip()

        if not password:
            while True:
                p1 = getpass.getpass("Enter Secure Password (min 8 chars): ")
                p2 = getpass.getpass("Confirm Password: ")
                if p1 != p2:
                    self.stdout.write(self.style.ERROR("Passwords do not match. Try again."))
                elif len(p1) < 8:
                    self.stdout.write(self.style.ERROR("Password must be at least 8 characters."))
                else:
                    password = p1
                    break

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'role': CustomUser.ROLE_OWNER,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_email_verified': True,
            }
        )

        user.set_password(password)
        user.role = CustomUser.ROLE_OWNER
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_email_verified = True
        user.save()

        AuditLog.objects.create(
            user=user,
            action="OWNER_ACCOUNT_PROVISIONED",
            details=f"Owner account {user.email} established securely via CLI."
        )

        status_text = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"\nBusiness Owner account {status_text} successfully: {user.email}"))
        self.stdout.write(self.style.SUCCESS("You can now access the full management suite at /portal/"))
