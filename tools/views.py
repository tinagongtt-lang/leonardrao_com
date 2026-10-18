from django.shortcuts import render


def index(request):
    return render(request, 'tools/index.html')


def timer(request):
    return render(request, 'tools/timer.html')


def stopwatch(request):
    return render(request, 'tools/stopwatch.html')


def base_converter(request):
    return render(request, 'tools/base_converter.html')
