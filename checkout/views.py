from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))
    
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51NNvZBAPy9Ym6myIaxoLj4xpa2znWq0W5GYo6HYUmg6OTA1sBuePmmIXa0otppKbPiHKyq1M5b5IawdtmPhdsQlK00Y1WWPTVf',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)