from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from core.models import Competition, Contestant, Vote, NFT, NFTCollection, RevenueDistribution
import os
from django.contrib import messages
from accounts.models import Profile, UserWallet
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from hiero.nft import mint_nft, associate_nft, transfer_nft
from hiero.ft import transfer_tokens
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@login_required(login_url='login')
@require_http_methods(["POST"])
def buy_ticket(request, nft_tier, competition_id):
    print("111")
    """
    Process ticket purchase for a specific competition and tier
    """
    try:
        # Get the competition
        competition = Competition.objects.get(id=competition_id)
        user = request.user
        # Get user's wallet address (you might want to store this in user profile)
        wallet_address = user.wallet.recipient_id#request.POST.get('wallet_address') or getattr(request.user.profile, 'wallet_address', None)
        print(user)
        
        #if not wallet_address:
        #    return JsonResponse({
        #        'success': False,
        #        'message': 'Wallet address not found. Please connect your wallet first.'
        #    }, status=400)
        #
        # Check if competition is available for ticket purchase
        if competition.status not in ['upcoming', 'registration_open', 'voting_open']:
            return JsonResponse({
                'success': False,
                'message': 'This competition is not available for ticket purchase.'
            }, status=400)
        
        # Get the NFT collection for this competition and tier
        try:
            nft_collection = NFTCollection.objects.get(
                competition=competition,
                nft_type=nft_tier.upper()  # Convert to uppercase to match choices
            )
        except NFTCollection.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'{nft_tier} tickets are not available for this competition.'
            }, status=404)
        
        # Check if there are available NFTs
        if nft_collection.is_sold_out():
            return JsonResponse({
                'success': False,
                'message': f'Sold out! No more {nft_tier} tickets available.'
            }, status=400)
        
        # Get the next available serial number
        next_serial = nft_collection.current_supply + 1
        
        # Simulate Hedera transaction (replace with actual Hedera SDK calls)
        transaction_result = simulate_hedera_transaction(
            wallet_address=wallet_address,
            nft_collection=nft_collection,
            serial_number=next_serial
        )
        
        if transaction_result['success']:
            # Create the NFT record
            nft = NFT.objects.create(
                collection=nft_collection,
                serial_number=next_serial,
                owner_wallet=wallet_address,
                is_available=False,
                price=nft_collection.get_default_price()
            )
            
            # Update collection supply
            nft_collection.current_supply = next_serial
            nft_collection.save()
            
            # Create revenue distribution record
            RevenueDistribution.objects.create(
                competition=competition,
                amount=nft_collection.get_default_price(),
                distribution_type='platform',
                recipient_wallet='platform_wallet_address',  # Your platform wallet
                transaction_hash=transaction_result['transaction_hash']
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully purchased {nft_tier} ticket for {competition.title}',
                'transaction_hash': transaction_result['transaction_hash'],
                'nft_serial': next_serial,
                'nft_id': f"{nft_collection.nft_id}/{next_serial}",
                'tier': nft_tier,
                'competition_title': competition.title
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Transaction failed: {transaction_result["error"]}'
            }, status=400)
            
    except Competition.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Competition not found.'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

def simulate_hedera_transaction(wallet_address, nft_collection, serial_number):
    """
    Simulate Hedera NFT transaction (replace with actual Hedera SDK implementation)
    """
    # This is a simulation - replace with actual Hedera SDK code
    import random
    import string
    
    # Simulate 90% success rate
    if random.random() > 0.1:  # 90% success rate
        return {
            'success': True,
            'transaction_hash': '0.0.' + ''.join(random.choices(string.digits, k=9)),
            'nft_id': f"{nft_collection.nft_id}/{serial_number}",
            'timestamp': datetime.now().isoformat()
        }
    else:
        return {
            'success': False,
            'error': 'Simulated transaction failure - insufficient funds'
        }

@login_required(login_url='login')
def nft_marketplace(request):
    """Display all available NFTs with supply information"""
    events = Competition.objects.all()
    collections = NFTCollection.objects.prefetch_related('nfts').all()
    available_nfts = NFT.objects.filter(is_available=True)
    competitions = Competition.objects.filter(
        status__in=['registration_open', 'voting_open', 'upcoming']
    ).prefetch_related(
        'contestant_set',
        'nftcollection_set',
        'nftcollection_set__nfts'
    ).order_by('date_time')

    available_nfts = NFT.objects.filter(
        is_available=True,
        collection__competition__status__in=['registration_open', 'voting_open', 'upcoming']
    ).select_related(
        'collection',
        'collection__competition'
    ).order_by('collection__competition__date_time')
    
    return render(request, 'core/nft.html', {
        'collections': collections,
        'nfts': available_nfts,
        'competitions':competitions,
        'available_nfts':available_nfts,
    })

def collection_detail(request, nft_type):
    """Display details for a specific collection"""
    collection = NFTCollection.objects.get(nft_type=nft_type)
    nfts_in_collection = collection.nfts.all()
    
    return render(request, 'collection_detail.html', {
        'collection': collection,
        'nfts': nfts_in_collection
    })

@login_required(login_url='login')
def buy_tickets(request, nft_id):
    nft=NFTCollection.objects.get(id=nft_id)
    user = request.user
    wallet = UserWallet.objects.get(user=user)
    if nft:
        competition = nft.competition
        if nft.max_supply > nft.current_supply:
            # Mint NFT TO THAT USER
            # eg Afrobeat Night
            ticket_metadata = {
                "name": f"Jamii Arena: {competition.title} - {nft.nft_type} Pass",
                "description": "NFT Ticket granting access and voting rights to the {competition.title}.",
                "external_url": "https://jamiiarena.com/events/",
                "attributes": [
                    {
                        "trait_type": "Event",
                        "value": f"{competition.title}"
                    },
                    {
                        "trait_type": "Date",
                        "value": f"{competition.date_time}"
                    },
                    {
                        "trait_type": "Venue",
                        "value": f"{competition.venue}"
                    },
                    {
                        "trait_type": "Seat Type",
                        "value": f"{nft.nft_type}"
                    },
                    {
                        "trait_type": "Voting Power",
                        "value": f"{nft.get_votes()}"
                    }
                ]
            }
            # Check if user has enough money in account
            profile = Profile.objects.get(user=user)
            if profile.funds >= int(nft.get_default_price):
                # Logic for Token Transfer to come here
                # 
                pass
            else:
                # Not Enough Funds to Facilitate this
                messages.warning(request, "You Don't have sufficient Balance in your account to buy this NFT, please recharge and try again.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # Check if user has already minted the same nft
            minted = NFT.objects.filter(owner_wallet=wallet.recipient_id, collection=nft)
            if minted:
                messages.warning(request, "You already have this Ticket in your Collections")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                nft_ = mint_nft(nft_token_id=nft.nft_id, metadata=ticket_metadata)
                if nft_:
                    assc=associate_nft(account_id=wallet.recipient_id, token_id=nft.nft_id, account_private_key=wallet.decrypt_key, nft_id=nft_)
                    if assc:
                        NFT.objects.create(collection=nft, serial_number=nft_, owner_wallet=wallet.recipient_id, price=int(nft.get_default_price))
                        messages.success(request, f"Congratulations, You now own {nft.get_title} Ticket, use it at the entrance of the venue!")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    else:
                        messages.warning(request, "An Error Occured while tranfering your Ticket to your Account, try again Later")
        else:
            # NFT max Supply has been hit
            pass


@login_required(login_url='login')
def voting(request):
    """
    Member must have attended the Event to be eligible to vote.
    Small Fee should be deducted for voting
    """
    user = request.user
    #perfomance = LivePerformance.objects.all()
    content = {
        #'perfomance':perfomance
    }

    return render(request, 'core/voting.html', content)

@login_required(login_url='login')
def governance(request):
    return render(request, 'core/dao.html')

@login_required(login_url='login')
def add_funds(request):
    # Simulate successful Payment when buying JMT for Demo
    # Disable Simulation and enable STK Push respectively for real Testing with Mpesa
    recipient_id = request.user.wallet.recipient_id
    if request.method == "POST":
        amount = request.POST['amount']
        # STK PUSH
        """
        Comes Here
        """
        # Transfer JMT after successful Payment
        token_transfer = transfer_tokens(recipient_id=recipient_id, amount=int(amount))
        if token_transfer['status'] == "success":
            # Record Activity on Activity Log
            messages.success(request, f'JMT has been purchased successfully and transfered to your wallet address: {recipient_id}')
        else:
            messages.warning(request, f"An error occured while completing your transaction, please try again later!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))