from django.contrib.auth.models import User
superadmin_name = 'drfadmin'
superadmin_password = 'drfpass'
if not User.objects.filter(username=superadmin_name).first():
    User.objects.create_superuser(superadmin_name, '', superadmin_password)
    print("Superuser created:"
          f"\nName: {superadmin_name}"
          f"\nPassword: {superadmin_password}"
    )
