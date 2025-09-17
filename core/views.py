from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from core.models import NFTTicket, LivePerformance, Competition, Contestant, TicketTier, Vote, NFT, NFTCollection
import os
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()


def can_user_vote(user_wallet, performance_id):
    # Check if the user owns any ticket for any tier of this performance
    return NFTTicket.objects.filter(
        owner_wallet=user_wallet,
        tier__performance_id=performance_id,
        status='sold'
    ).exists()

@require_GET  # Only allow GET requests
def check_nft_availability(request, nft_type, serial_number):
    """API endpoint to check if an NFT is available for purchase"""
    try:
        nft = NFT.objects.get(
            collection__nft_type=nft_type,
            serial_number=serial_number
        )
        
        response_data = {
            'available': nft.is_available,
            'price': float(nft.price),
            'nft_type': nft_type,
            'serial_number': serial_number,
            'collection_name': nft.collection.name
        }
        
        return JsonResponse(response_data)
        
    except NFT.DoesNotExist:
        return JsonResponse({
            'available': False,
            'error': 'NFT not found',
            'nft_type': nft_type,
            'serial_number': serial_number
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'available': False,
            'error': str(e)
        }, status=500)
    
def nft(request):
    return render(request, 'core/nft.html')

@login_required(login_url='login')
def nft_marketplace(request):
    """Display all available NFTs with supply information"""
    collections = NFTCollection.objects.prefetch_related('nfts').all()
    available_nfts = NFT.objects.filter(is_available=True)
    
    return render(request, 'core/nft.html', {
        'collections': collections,
        'nfts': available_nfts
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
def voting(request):
    """
    Member must have attended the Event to be eligible to vote.
    Small Fee should be deducted for voting
    """
    user = request.user
    # Efficient Query with Strategy 1 (Separate Collections)
    performance = LivePerformance.objects.get(id=1)
    vvip_tier = performance.tiers.get(tier='vvip')
    vvip_holders = NFTTicket.objects.filter(tier=vvip_tier)

    # Inefficient Query with Strategy 2 (Single Collection)
    # You would have to check each ticket's metadata IPFS hash to find the tier.
    wallet_id = user.wallet.recipient_id
    my_tickets = NFTTicket.objects.filter(owner_wallet=wallet_id)
    perfomance = LivePerformance.objects.all()
    content = {
        'perfomance':perfomance
    }

    return render(request, 'core/voting.html', content)

@login_required(login_url='login')
def governance(request):
    return render(request, 'core/dao.html')