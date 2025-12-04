from django.db import transaction
from users.models import Round, InvestorPipeline, Incubator, Startup

def create_round_with_incubators(startup: Startup, round_data: dict, incubator_commits: list) -> Round:
    """
    Creates a fundraising Round and registers associated Incubators as committed investors.

    Args:
        startup (Startup): The startup creating the round.
        round_data (dict): Dictionary containing round details (name, target_amount, etc.).
        incubator_commits (list): List of dicts with incubator commitments.
            Example: [{'incubator_id': 1, 'amount': 50000, 'incubator_name': 'Techstars'}]

    Returns:
        Round: The created Round object.
    """
    
    with transaction.atomic():
        # 1. Create Round
        # Ensure 'startup' is not in round_data to avoid duplication if passed
        round_data.pop('startup', None)
        
        # Set default status if not provided (though model default is True)
        if 'is_open' not in round_data:
            round_data['is_open'] = True

        new_round = Round.objects.create(startup=startup, **round_data)

        # 2. Process Incubator Commits
        incubator_ids_to_associate = []

        for commit in incubator_commits:
            incubator_id = commit.get('incubator_id')
            amount = commit.get('amount')
            incubator_name = commit.get('incubator_name')
            
            # Basic validation
            if not incubator_id or not amount:
                continue

            incubator_ids_to_associate.append(incubator_id)

            # Create Investor (InvestorPipeline)
            # We assume the incubator has an email, or we generate/fetch one.
            # For now, we'll try to fetch the incubator to get the real email if possible,
            # otherwise use a placeholder or the one provided.
            
            investor_email = commit.get('email', '')
            if not investor_email:
                try:
                    incubator = Incubator.objects.get(id=incubator_id)
                    # Try to get email from profile user
                    investor_email = incubator.profile.user.email
                except Incubator.DoesNotExist:
                    investor_email = f"contact@incubator{incubator_id}.com" # Fallback

            InvestorPipeline.objects.create(
                startup=startup,
                round=new_round,
                investor_name=incubator_name or f"Incubator {incubator_id}",
                investor_email=investor_email,
                stage=InvestorPipeline.COMMITTED,
                ticket_size=amount,
                notes=f"Auto-generated from Incubator commitment for round {new_round.name}"
            )

        # 3. Operational Association
        # Ensure the startup is associated with these incubators
        if incubator_ids_to_associate:
            # We use .add() to ensure we don't remove existing associations
            # The requirement says "asegúrate de que... esté vinculada... (si no lo estaba antes)"
            # So .add() is appropriate.
            # However, the user mentioned using the endpoint logic which uses .set().
            # But .set() replaces. If we want to ADD, we should use .add().
            # If the user meant "ensure these are THE incubators", then .set().
            # But typically creating a round shouldn't remove other incubator associations.
            # I will use .add() to be safe and logical.
            
            # Verify incubators exist before adding to avoid errors
            valid_incubators = Incubator.objects.filter(id__in=incubator_ids_to_associate)
            startup.incubators.add(*valid_incubators)

        return new_round
