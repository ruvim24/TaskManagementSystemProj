from DjangoProject.celery import app


@app.task
def send_users_top_tasks_every_week():
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    from django.contrib.auth.models import User

    users = User.objects.all()

    results = {
        "users_found": users.count(),
        "emails_sent": [],
        "emails_failed": [],
        'users_skipped_no_email': [],
        'users_no_tasks': [],
        "errors": []
    }

    if not users.exists():
        print("No users found.")
        return
    print(f'Found {users.count()} users.')

    for user in users:
        print(f"Processing user: {user.username}")
        top_tasks = (
            user.tasks
            .filter(status="open", time_logs__duration__isnull=False)
            .order_by("time_logs__duration")[:20]
        )

        if not top_tasks:
            print(f"No tasks found for user {user.username}.")
            results['users_no_tasks'] = + 1
            continue

        if user.email is None:
            print(f"User {user.username} has no email, skipping...")
            results['users_skipped_no_email'] = + 1
            continue

        context = {
            'user': user,
            'top_tasks': top_tasks,
        }

        html_content = render_to_string('tasks/email/top_tasks_report.html', context)

        msg = EmailMessage(
            'Subiect: Raport Top 20 Task-uri',
            html_content,
            'expeditor@exemplu.com',
            [user.email],
        )
        msg.content_subtype = "html"

        try:
            was_sent = msg.send(fail_silently=False)
            if was_sent == 1:
                print(f"Email sent successfully to {user.username} ({user.email}) with the task report.")
                results['emails_sent'] = + 1
            else:
                print(f"Failed to send email to {user.username} ({user.email}). Code: {was_sent}")
                results['emails_failed'] = + 1
        except Exception as e:
            print(f"An exception occurred while sending the email to {user.username}: {e}")
            results['errors'] = + 1

    return results
