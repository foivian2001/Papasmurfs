from django.shortcuts import render


def home(request):
    """Display the Papasmurfs homepage."""
    return render(request, "core/home.html")
