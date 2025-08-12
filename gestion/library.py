from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from dateutil.relativedelta import relativedelta
import csv
from django.db import transaction
from decimal import Decimal, InvalidOperation

from .forms import  CustomAuthenticationForm, CustomUserChangeForm,PasswordResetForm, NewPasswordForm
from .models import Parent, AnneeScolaire, MoisPaiement, Classe, Option, Section, Paiement, Depense, Eleve, Frais, Inscription, TRANCHE_CHOICES
from .forms import DepenseForm, SuiviFinancierForm, FraisForm, PaiementForm, FiltragePaiementForm, EleveForm
from django.core.serializers.json import DjangoJSONEncoder
from .access_control import check_section_access, role_required, financier_required
import random
import string
from django.contrib.auth import login
from .forms import CustomUserCreationForm

from django import forms  # <- Cette ligne était manquante
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import CustomUser

# views.py
import json
import pandas as pd
from django.http import HttpResponse
from django.views import View
from io import BytesIO
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

from .access_control import (
    directeur_required,
    prefet_required,
    itm_required,
    filter_by_user_role,
    check_section_access,
    get_accessible_sections,
financier_required,
finance_required,
prefets_required,
admin_required,

)
# vu modifier apaiement
from .forms import ModifierPaiementForm
from django.db.models import Sum
from django.http import JsonResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import Paiement, AnneeScolaire
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Section, Option, Classe
from .access_control import get_accessible_sections, filter_by_user_role

from .access_control import get_accessible_sections, filter_by_user_role
from .access_control import (
    directeur_required,
    prefet_required,
    itm_required,
    filter_by_user_role,
    check_section_access,
    get_accessible_sections
)
from .access_control import filter_by_user_role, get_accessible_sections
import locale
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from .models import Paiement, Depense
from .forms import SuiviFinancierForm

from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Paiement, Depense
from datetime import datetime
import json
from .access_control import get_accessible_sections
from .access_control import get_accessible_sections, filter_by_user_role

from django.db.models import Sum, Count, Max
from django.shortcuts import render, get_object_or_404
from .models import Classe, Eleve, Paiement, Frais
from collections import defaultdict

from django.db.models.functions import TruncMonth


from rest_framework import viewsets
from .models import HistoriqueAction
from .serializers import HistoriqueActionSerializer



from django.utils.timezone import make_aware
from datetime import datetime
from .models import HistoriqueAction, Paiement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Dans gestion/views.py
from django.shortcuts import render
from django.db.models import Q
from .models import Section, Classe, Frais, Paiement, HistoriqueAction
from .access_control import get_accessible_sections

# Dans gestion/views.py
from django.shortcuts import render
from .models import Paiement, Frais, HistoriqueAction

from .models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from gestion.apis import *
from django.db.models import Sum, Count, Max, Q, Prefetch, F
from django.db.models.functions import TruncMonth
from gestion.utils import recuperer_annee_active
from django.db.models.functions import TruncMonth


