import stripe
from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def create_stripe_price(stripe_product_id, amount):
  """Создаём stripe цену"""
  return stripe.Price.create(
    currency="rub",
    unit_amount=int(amount * 100),
    product=stripe_product_id,
  )

def create_stripe_session(price):
  """Создает сессию на оплату в страйпе"""
  session = stripe.checkout.Session.create(
    success_url="http://127.0.0.1:8000/",
    line_items=[{"price": price.get("id"), "quantity": 1}],
    mode="payment",
  )
  return session.get("id"), session.get("url")


def create_stripe_product(instance):
  """Создаем stripe продукт"""
  title_product = (
    f"{instance.paid_course}" if instance.paid_course else f"{instance.paid_lesson}"
  )
  stripe_product = stripe.Product.create(name=f"{title_product}")
  return stripe_product.get("id")


class CreateCheckoutSessionView:
    pass