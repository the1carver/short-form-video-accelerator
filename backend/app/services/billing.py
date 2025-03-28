import logging
import json
from typing import Dict, Any, Optional
import stripe
from ..config import settings
from ..database import db, create_item, get_item, update_item

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class BillingService:
    def __init__(self):
        self.stripe_client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Stripe client"""
        try:
            if settings.stripe_api_key:
                stripe.api_key = settings.stripe_api_key
                self.stripe_client = stripe
                logger.info("Stripe client initialized successfully")
            else:
                logger.warning("Stripe API key not provided, billing operations will be simulated")
        except Exception as e:
            logger.error(f"Error initializing Stripe client: {str(e)}")
    
    async def create_customer(self, user_id: str, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new customer in Stripe.
        
        Args:
            user_id: ID of the user
            email: Email address of the customer
            name: Name of the customer (optional)
            
        Returns:
            Customer data
        """
        logger.info(f"Creating Stripe customer for user ID: {user_id}")
        
        try:
            if self.stripe_client:
                # Create customer in Stripe
                customer = self.stripe_client.Customer.create(
                    email=email,
                    name=name,
                    metadata={"user_id": user_id}
                )
                
                logger.info(f"Created Stripe customer: {customer.id}")
                
                # Save customer ID to user record
                user = await get_item(db.users, user_id)
                if user:
                    await update_item(db.users, user_id, {"stripe_customer_id": customer.id})
                
                return {
                    "customer_id": customer.id,
                    "email": customer.email,
                    "name": customer.name,
                    "success": True
                }
            else:
                # Simulate customer creation for development
                simulated_customer_id = f"cus_sim_{user_id}"
                
                # Save simulated customer ID to user record
                user = await get_item(db.users, user_id)
                if user:
                    await update_item(db.users, user_id, {"stripe_customer_id": simulated_customer_id})
                
                return {
                    "customer_id": simulated_customer_id,
                    "email": email,
                    "name": name,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a customer.
        
        Args:
            user_id: ID of the user
            plan_id: ID of the subscription plan
            payment_method_id: ID of the payment method (optional)
            
        Returns:
            Subscription data
        """
        logger.info(f"Creating subscription for user ID: {user_id} with plan: {plan_id}")
        
        try:
            # Get user record
            user = await get_item(db.users, user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User not found: {user_id}"
                }
            
            # Get customer ID
            customer_id = user.get("stripe_customer_id")
            if not customer_id:
                return {
                    "success": False,
                    "error": "User does not have a Stripe customer ID"
                }
            
            if self.stripe_client:
                # Attach payment method to customer if provided
                if payment_method_id:
                    self.stripe_client.PaymentMethod.attach(
                        payment_method_id,
                        customer=customer_id
                    )
                    
                    # Set as default payment method
                    self.stripe_client.Customer.modify(
                        customer_id,
                        invoice_settings={
                            "default_payment_method": payment_method_id
                        }
                    )
                
                # Create subscription
                subscription = self.stripe_client.Subscription.create(
                    customer=customer_id,
                    items=[{"price": plan_id}],
                    expand=["latest_invoice.payment_intent"]
                )
                
                logger.info(f"Created Stripe subscription: {subscription.id}")
                
                # Save subscription ID to user record
                await update_item(db.users, user_id, {"stripe_subscription_id": subscription.id})
                
                return {
                    "subscription_id": subscription.id,
                    "status": subscription.status,
                    "current_period_end": subscription.current_period_end,
                    "success": True
                }
            else:
                # Simulate subscription creation for development
                simulated_subscription_id = f"sub_sim_{user_id}_{plan_id}"
                
                # Get plan details (simulated)
                plan_details = self._get_simulated_plan_details(plan_id)
                
                # Save simulated subscription ID to user record
                await update_item(db.users, user_id, {"stripe_subscription_id": simulated_subscription_id})
                
                return {
                    "subscription_id": simulated_subscription_id,
                    "status": "active",
                    "current_period_end": 1735689600,  # One month from now (approximately)
                    "plan": plan_details,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Cancel a subscription for a customer.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Cancellation result
        """
        logger.info(f"Cancelling subscription for user ID: {user_id}")
        
        try:
            # Get user record
            user = await get_item(db.users, user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User not found: {user_id}"
                }
            
            # Get subscription ID
            subscription_id = user.get("stripe_subscription_id")
            if not subscription_id:
                return {
                    "success": False,
                    "error": "User does not have an active subscription"
                }
            
            if self.stripe_client:
                # Cancel subscription in Stripe
                subscription = self.stripe_client.Subscription.delete(subscription_id)
                
                logger.info(f"Cancelled Stripe subscription: {subscription_id}")
                
                # Update user record
                await update_item(db.users, user_id, {"stripe_subscription_id": None})
                
                return {
                    "subscription_id": subscription_id,
                    "status": subscription.status,
                    "success": True
                }
            else:
                # Simulate subscription cancellation for development
                
                # Update user record
                await update_item(db.users, user_id, {"stripe_subscription_id": None})
                
                return {
                    "subscription_id": subscription_id,
                    "status": "canceled",
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get subscription details for a customer.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Subscription details
        """
        logger.info(f"Getting subscription for user ID: {user_id}")
        
        try:
            # Get user record
            user = await get_item(db.users, user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User not found: {user_id}"
                }
            
            # Get subscription ID
            subscription_id = user.get("stripe_subscription_id")
            if not subscription_id:
                return {
                    "success": True,
                    "has_subscription": False
                }
            
            if self.stripe_client:
                # Get subscription from Stripe
                subscription = self.stripe_client.Subscription.retrieve(subscription_id)
                
                # Get plan details
                plan = None
                if subscription.items.data:
                    price = subscription.items.data[0].price
                    plan = {
                        "id": price.id,
                        "name": price.nickname,
                        "amount": price.unit_amount / 100,  # Convert from cents to dollars
                        "currency": price.currency,
                        "interval": price.recurring.interval
                    }
                
                return {
                    "subscription_id": subscription_id,
                    "status": subscription.status,
                    "current_period_end": subscription.current_period_end,
                    "plan": plan,
                    "has_subscription": True,
                    "success": True
                }
            else:
                # Simulate subscription details for development
                
                # Get plan details (simulated)
                plan_details = self._get_simulated_plan_details("price_sim_professional")
                
                return {
                    "subscription_id": subscription_id,
                    "status": "active",
                    "current_period_end": 1735689600,  # One month from now (approximately)
                    "plan": plan_details,
                    "has_subscription": True,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_plans(self) -> Dict[str, Any]:
        """
        Get available subscription plans.
        
        Returns:
            List of available plans
        """
        logger.info("Getting available subscription plans")
        
        try:
            if self.stripe_client:
                # Get plans from Stripe
                prices = self.stripe_client.Price.list(
                    active=True,
                    limit=10,
                    expand=["data.product"]
                )
                
                plans = []
                for price in prices.data:
                    plans.append({
                        "id": price.id,
                        "name": price.nickname or price.product.name,
                        "description": price.product.description,
                        "amount": price.unit_amount / 100,  # Convert from cents to dollars
                        "currency": price.currency,
                        "interval": price.recurring.interval
                    })
                
                return {
                    "plans": plans,
                    "success": True
                }
            else:
                # Simulate plans for development
                plans = [
                    {
                        "id": "price_sim_basic",
                        "name": "Basic",
                        "description": "5 videos per month",
                        "amount": 249,
                        "currency": "usd",
                        "interval": "month"
                    },
                    {
                        "id": "price_sim_professional",
                        "name": "Professional",
                        "description": "15 videos per month",
                        "amount": 599,
                        "currency": "usd",
                        "interval": "month"
                    },
                    {
                        "id": "price_sim_enterprise",
                        "name": "Enterprise",
                        "description": "50 videos per month",
                        "amount": 1499,
                        "currency": "usd",
                        "interval": "month"
                    }
                ]
                
                return {
                    "plans": plans,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error getting available plans: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_checkout_session(
        self,
        user_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create a checkout session for a customer.
        
        Args:
            user_id: ID of the user
            plan_id: ID of the subscription plan
            success_url: URL to redirect to on successful payment
            cancel_url: URL to redirect to on cancelled payment
            
        Returns:
            Checkout session data
        """
        logger.info(f"Creating checkout session for user ID: {user_id} with plan: {plan_id}")
        
        try:
            # Get user record
            user = await get_item(db.users, user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User not found: {user_id}"
                }
            
            # Get customer ID
            customer_id = user.get("stripe_customer_id")
            if not customer_id:
                return {
                    "success": False,
                    "error": "User does not have a Stripe customer ID"
                }
            
            if self.stripe_client:
                # Create checkout session in Stripe
                session = self.stripe_client.checkout.Session.create(
                    customer=customer_id,
                    payment_method_types=["card"],
                    line_items=[{
                        "price": plan_id,
                        "quantity": 1
                    }],
                    mode="subscription",
                    success_url=success_url,
                    cancel_url=cancel_url
                )
                
                logger.info(f"Created Stripe checkout session: {session.id}")
                
                return {
                    "session_id": session.id,
                    "url": session.url,
                    "success": True
                }
            else:
                # Simulate checkout session for development
                simulated_session_id = f"cs_sim_{user_id}_{plan_id}"
                simulated_url = f"{success_url}?session_id={simulated_session_id}"
                
                return {
                    "session_id": simulated_session_id,
                    "url": simulated_url,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_simulated_plan_details(self, plan_id: str) -> Dict[str, Any]:
        """
        Get simulated plan details.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            Plan details
        """
        plans = {
            "price_sim_basic": {
                "id": "price_sim_basic",
                "name": "Basic",
                "description": "5 videos per month",
                "amount": 249,
                "currency": "usd",
                "interval": "month"
            },
            "price_sim_professional": {
                "id": "price_sim_professional",
                "name": "Professional",
                "description": "15 videos per month",
                "amount": 599,
                "currency": "usd",
                "interval": "month"
            },
            "price_sim_enterprise": {
                "id": "price_sim_enterprise",
                "name": "Enterprise",
                "description": "50 videos per month",
                "amount": 1499,
                "currency": "usd",
                "interval": "month"
            }
        }
        
        return plans.get(plan_id, {
            "id": plan_id,
            "name": "Unknown Plan",
            "description": "Unknown plan details",
            "amount": 0,
            "currency": "usd",
            "interval": "month"
        })

# Create global billing service instance
billing_service = BillingService()
