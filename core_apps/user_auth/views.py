from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from loguru import logger

# Simple of loguru of docs
# class TestLoggingView(View):
#     def get(self, request):
#         logger.debug("this is debug")
#         logger.info("this is info")
#         logger.warning("this is warning")
#         logger.error("this is error")
#         logger.critical("this is critical")
#         return JsonResponse({"message": "Done!"})
