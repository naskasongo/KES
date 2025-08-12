# Mise à jour du formulaire de filtrage avec contrôle d'accès
class FiltragePaiementForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Initialisation des champs avec filtrage par rôle
        allowed_sections = get_accessible_sections(self.user)
        
        # Appliquer le filtrage aux querysets
        self.fields['section'].queryset = allowed_sections
        self.fields['option'].queryset = Option.objects.filter(section__in=allowed_sections)
        self.fields['classe'].queryset = Classe.objects.filter(
            Q(section__in=allowed_sections) | 
            Q(option__section__in=allowed_sections)
        ).distinct()
        
        # Filtrer les frais selon les classes autorisées
        allowed_classes = self.fields['classe'].queryset
        self.fields['frais'].queryset = Frais.objects.filter(classes__in=allowed_classes).distinct()
        
        # Si l'utilisateur n'est pas admin, masquer les options pour lesquelles il n'a pas accès
        if not (self.user.is_superuser or getattr(self.user, 'role', None) == 'admin'):
            self.fields['section'].queryset = allowed_sections
            self.fields['option'].queryset = Option.objects.filter(section__in=allowed_sections)
            self.fields['classe'].queryset = Classe.objects.filter(
                Q(section__in=allowed_sections) | 
                Q(option__section__in=allowed_sections)
            ).distinct()
            self.fields['frais'].queryset = Frais.objects.filter(classes__in=allowed_classes).distinct()

    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    option = forms.ModelChoiceField(
        queryset=Option.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    frais = forms.ModelChoiceField(
        queryset=Frais.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ModifierPaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['eleve', 'frais', 'mois', 'tranche', 'montant_paye', 'recu_numero']  # 添加recu_numero字段
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将收据编号字段设为只读
        self.fields['recu_numero'].disabled = True
