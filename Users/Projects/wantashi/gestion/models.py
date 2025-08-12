class Paiement(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    frais = models.ForeignKey(Frais, on_delete=models.CASCADE)
    mois = models.CharField(max_length=255, choices=MoisPaiement.choices, blank=True, null=True)
    tranche = models.CharField(max_length=50, choices=TRANCHE_CHOICES, blank=True, null=True)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    solde_restant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compensation_details = models.JSONField(default=dict)
    # 添加收据编号字段
    recu_numero = models.CharField(max_length=50, blank=True, null=True)  # 新增字段
    
    def save(self, *args, **kwargs):
        # 生成收据编号（仅在创建时生成）
        if not self.pk and not self.recu_numero:
            self.recu_numero = self.generate_recu_numero()
            
        # 处理每月余额更新逻辑
        if self.frais.type_frais == "Mensuel":
            self.update_solde_mois_precedent()
            
        super().save(*args, **kwargs)