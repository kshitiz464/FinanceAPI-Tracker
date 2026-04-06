"""
Management command to seed the database with realistic demo data.
Creates 3 users (admin, analyst, viewer) and 50+ financial transactions.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # Clear existing data first
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from api.models import User, Transaction


class Command(BaseCommand):
    help = 'Seed the database with demo users and financial transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Transaction.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating demo users...')
        users = self._create_users()

        self.stdout.write('Creating demo transactions...')
        self._create_transactions(users)

        self.stdout.write(self.style.SUCCESS(
            '\nDatabase seeded successfully!'
            f'\n   Users created: {len(users)}'
            f'\n   Transactions created: {Transaction.objects.count()}'
            f'\n\n   Login credentials:'
            f'\n   -----------------------------------'
            f'\n   admin_user   / Admin@123   (role: admin)'
            f'\n   analyst_user / Analyst@123 (role: analyst)'
            f'\n   viewer_user  / Viewer@123  (role: viewer)'
        ))

    def _create_users(self):
        users = {}
        user_data = [
            {'username': 'admin_user', 'email': 'admin@finance.com',
             'password': 'Admin@123', 'role': 'admin'},
            {'username': 'analyst_user', 'email': 'analyst@finance.com',
             'password': 'Analyst@123', 'role': 'analyst'},
            {'username': 'viewer_user', 'email': 'viewer@finance.com',
             'password': 'Viewer@123', 'role': 'viewer'},
        ]
        for data in user_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'role': data['role'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f'  Created: {user.username} ({user.role})')
            else:
                self.stdout.write(f'  Exists:  {user.username} ({user.role})')
            users[data['role']] = user
        return users

    def _create_transactions(self, users):
        # Only create if no transactions exist
        if Transaction.objects.exists():
            self.stdout.write('  Transactions already exist, skipping...')
            return

        admin = users['admin']
        today = date.today()

        # Realistic finance categories
        income_categories = [
            ('Salary', 45000, 55000),
            ('Freelance', 5000, 25000),
            ('Investment Returns', 2000, 15000),
            ('Rental Income', 8000, 12000),
            ('Bonus', 10000, 30000),
            ('Consulting', 8000, 20000),
            ('Dividends', 1000, 5000),
        ]

        expense_categories = [
            ('Rent', 10000, 20000),
            ('Groceries', 2000, 8000),
            ('Utilities', 1000, 3000),
            ('Transportation', 1500, 5000),
            ('Healthcare', 500, 10000),
            ('Entertainment', 500, 5000),
            ('Education', 2000, 15000),
            ('Insurance', 3000, 8000),
            ('Dining Out', 500, 4000),
            ('Shopping', 1000, 10000),
            ('Travel', 5000, 30000),
            ('Subscriptions', 500, 2000),
            ('Maintenance', 1000, 5000),
            ('Office Supplies', 500, 3000),
        ]

        transactions = []

        # Generate 6 months of data
        for month_offset in range(6):
            month_date = today - timedelta(days=30 * month_offset)

            # 1-2 income entries per month
            for _ in range(random.randint(1, 3)):
                cat, min_amt, max_amt = random.choice(income_categories)
                day = random.randint(1, 28)
                t_date = month_date.replace(day=day)
                if t_date > today:
                    t_date = today

                transactions.append(Transaction(
                    amount=round(random.uniform(min_amt, max_amt), 2),
                    type='income',
                    category=cat,
                    date=t_date,
                    description=f'{cat} for {t_date.strftime("%B %Y")}',
                    created_by=admin,
                ))

            # 3-6 expense entries per month
            for _ in range(random.randint(3, 6)):
                cat, min_amt, max_amt = random.choice(expense_categories)
                day = random.randint(1, 28)
                t_date = month_date.replace(day=day)
                if t_date > today:
                    t_date = today

                transactions.append(Transaction(
                    amount=round(random.uniform(min_amt, max_amt), 2),
                    type='expense',
                    category=cat,
                    date=t_date,
                    description=f'{cat} payment — {t_date.strftime("%B %Y")}',
                    created_by=admin,
                ))

        # Bulk create for performance
        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'  Created {len(transactions)} transactions')
