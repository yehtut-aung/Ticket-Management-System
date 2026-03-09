from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Ticket, TicketComment
from .forms import TicketForm, TicketUpdateForm, CommentForm
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    user = request.user
    profile = user.profile
    
    # Different dashboard views based on role
    if profile.is_admin():
        # Admin sees all tickets
        tickets = Ticket.objects.all().order_by('-created_at')
        total_tickets = tickets.count()
        open_tickets = tickets.filter(status='open').count()
        in_progress = tickets.filter(status='in_progress').count()
        resolved = tickets.filter(status='resolved').count()
        
    elif profile.is_agent():
        # Agent sees tickets assigned to them
        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')
        total_tickets = tickets.count()
        open_tickets = tickets.filter(status='open').count()
        in_progress = tickets.filter(status='in_progress').count()
        resolved = tickets.filter(status='resolved').count()
        
    else:  # Customer
        # Customer sees only their own tickets
        tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
        total_tickets = tickets.count()
        open_tickets = tickets.filter(status='open').count()
        in_progress = tickets.filter(status='in_progress').count()
        resolved = tickets.filter(status='resolved').count()
    
    context = {
        'tickets': tickets[:5],  # Show only 5 most recent
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress': in_progress,
        'resolved': resolved,
        'user_role': profile.get_role_display(),
    }
    return render(request, 'tickets/dashboard.html', context)

@login_required
def ticket_list(request):
    user = request.user
    profile = user.profile
    
    if profile.is_admin():
        tickets = Ticket.objects.all().order_by('-created_at')
    elif profile.is_agent():
        tickets = Ticket.objects.filter(assigned_to=user).order_by('-created_at')
    else:
        tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)
    
    # Pagination
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tickets/ticket_list.html', {'page_obj': page_obj})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user
    profile = user.profile
    
    # Check permissions
    if not (profile.is_admin() or 
            profile.is_agent() and ticket.assigned_to == user or
            ticket.created_by == user):
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('dashboard')
    
    # Handle comments
    if request.method == 'POST' and 'comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.user = user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    # Handle status update (agents and admin only)
    elif request.method == 'POST' and 'update_status' in request.POST:
        if profile.is_admin() or profile.is_agent():
            new_status = request.POST.get('status')
            ticket.status = new_status
            ticket.save()
            messages.success(request, f'Ticket status updated to {new_status}!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    comment_form = CommentForm()
    comments = ticket.comments.all()
    
    # Check if user can update the ticket
    can_update = profile.is_admin() or (profile.is_agent() and ticket.assigned_to == user)
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'can_update': can_update,
    }
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketForm()
    
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user
    profile = user.profile
    
    # Check permissions
    if not (profile.is_admin() or (profile.is_agent() and ticket.assigned_to == user)):
        messages.error(request, "You don't have permission to update this ticket.")
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketUpdateForm(instance=ticket, user=user)
    
    return render(request, 'tickets/update_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def assign_ticket(request, ticket_id):
    if not request.user.profile.is_admin():
        messages.error(request, "Only admins can assign tickets.")
        return redirect('ticket_detail', ticket_id=ticket_id)
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    agents = User.objects.filter(profile__role='agent')
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent')
        if agent_id:
            agent = get_object_or_404(User, id=agent_id)
            ticket.assigned_to = agent
            ticket.status = 'in_progress'
            ticket.save()
            messages.success(request, f'Ticket assigned to {agent.username}')
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    return render(request, 'tickets/assign_ticket.html', {'ticket': ticket, 'agents': agents})