import re

filepath = r"c:\Users\USER\Desktop\ARISK V002\apps\credit_risk\models.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_model = """class CarteraCreditoCarga(models.Model):
    # Metadatos de Carga
    fecha_corte = models.DateField("Fecha de Corte", null=True, blank=True)
    fecha_carga = models.DateTimeField("Fecha de Carga", auto_now_add=True)
    
    n = models.CharField("Registro", max_length=50, blank=True, null=True)
    ncl = models.CharField("Apellidos y Nombres / Razón Social", max_length=255, blank=True, null=True)
    fnac = models.DateField("Fecha de Nacimiento", null=True, blank=True)
    gen = models.CharField("Género", max_length=50, blank=True, null=True)
    ec = models.CharField("Estado Civil", max_length=50, blank=True, null=True)
    emp = models.CharField("Sigla de la Empresa", max_length=255, blank=True, null=True)
    csoc = models.CharField("Código Socio", max_length=50, blank=True, null=True)
    pr = models.CharField("Partida Registral", max_length=100, blank=True, null=True)
    tid = models.CharField("Tipo de Documento", max_length=50, blank=True, null=True)
    nid = models.CharField("Número de Documento", max_length=50, blank=True, null=True)
    tper = models.CharField("Tipo de Persona", max_length=50, blank=True, null=True)
    dom = models.CharField("Domicilio", max_length=500, blank=True, null=True)
    rco = models.CharField("Relación Laboral", max_length=100, blank=True, null=True)
    cal = models.CharField("Clasificación del Deudor", max_length=50, blank=True, null=True)
    calint = models.CharField("Clasif Alineamiento", max_length=50, blank=True, null=True)
    cage = models.CharField("Código de Agencia", max_length=50, blank=True, null=True)
    mon = models.CharField("Moneda", max_length=50, blank=True, null=True)
    ccr = models.CharField("Número de Crédito", max_length=100, blank=True, null=True)
    tcr = models.CharField("Tipo de Crédito", max_length=100, blank=True, null=True)
    stcr = models.CharField("Sub Tipo de Crédito", max_length=100, blank=True, null=True)
    fot = models.DateField("Fecha de Desembolso", null=True, blank=True)
    morg = models.DecimalField("Monto de Desembolso", max_digits=18, decimal_places=4, default=0)
    tea = models.DecimalField("Tasa de Interés Anual", max_digits=18, decimal_places=4, default=0)
    skcr = models.DecimalField("Saldo de Colocaciones", max_digits=18, decimal_places=4, default=0)
    cc = models.CharField("Cuenta Contable", max_length=100, blank=True, null=True)
    kvi = models.DecimalField("Capital vigente", max_digits=18, decimal_places=4, default=0)
    kre = models.DecimalField("Capital Reestructurado", max_digits=18, decimal_places=4, default=0)
    krf = models.DecimalField("Capital Refinanciado", max_digits=18, decimal_places=4, default=0)
    kve = models.DecimalField("Capital Vencido", max_digits=18, decimal_places=4, default=0)
    kju = models.DecimalField("Capital en Cobranza Judicial", max_digits=18, decimal_places=4, default=0)
    kco = models.DecimalField("Capital Contingente", max_digits=18, decimal_places=4, default=0)
    cco = models.CharField("Cta Contable Cap Contigente", max_length=100, blank=True, null=True)
    dak = models.IntegerField("Días de Mora", null=True, blank=True)
    sgp = models.DecimalField("Saldos Garantías Preferidas", max_digits=18, decimal_places=4, default=0)
    sga = models.DecimalField("Saldos Garantías Autoliq", max_digits=18, decimal_places=4, default=0)
    pvr = models.DecimalField("Provisiones Requeridas", max_digits=18, decimal_places=4, default=0)
    pci = models.DecimalField("Provisiones Constituidas", max_digits=18, decimal_places=4, default=0)
    scc = models.DecimalField("Saldo Créditos Castigados", max_digits=18, decimal_places=4, default=0)
    ccc = models.CharField("Cta Contable Cred Castigado", max_length=100, blank=True, null=True)
    sin = models.DecimalField("Rendimiento Devengado", max_digits=18, decimal_places=4, default=0)
    sis = models.DecimalField("Intereses en Suspenso", max_digits=18, decimal_places=4, default=0)
    sid = models.DecimalField("Ingresos Diferidos", max_digits=18, decimal_places=4, default=0)
    tpr = models.CharField("Tipo de Producto", max_length=100, blank=True, null=True)
    ncpr = models.IntegerField("Número Cuotas Prog", null=True, blank=True)
    ncpa = models.IntegerField("Número Cuotas Pagadas", null=True, blank=True)
    pcuo = models.CharField("Periodicidad", max_length=50, blank=True, null=True)
    dgr = models.IntegerField("Periodo de Gracia", null=True, blank=True)
    fvgo = models.DateField("Fecha Venc Orig", null=True, blank=True)
    fvga = models.DateField("Fecha Venc Actual", null=True, blank=True)
    ssc = models.DecimalField("Saldo Cred Sustitución", max_digits=18, decimal_places=4, default=0)
    ssg = models.DecimalField("Saldo Cred Sin Cobertura", max_digits=18, decimal_places=4, default=0)
    scr = models.DecimalField("Saldo Cap Reprogramados", max_digits=18, decimal_places=4, default=0)
    skco = models.DecimalField("Saldo Cap Cta Orden COVID", max_digits=18, decimal_places=4, default=0)
    scor = models.CharField("Sub cuenta de Orden", max_length=100, blank=True, null=True)
    sinc = models.DecimalField("Rend Devengado COVID", max_digits=18, decimal_places=4, default=0)
    scs = models.DecimalField("Saldo Garantías Sustitución", max_digits=18, decimal_places=4, default=0)

    class Meta:
        verbose_name = "Carga Masiva - Cartera de Crédito"
        verbose_name_plural = "Cargas Masivas - Cartera de Créditos"

    def __str__(self):
        return f"{self.ncl} - Cred: {self.ccr}"
"""

# Replace everything from `class CarteraCreditoCarga` to the end of the file.
new_content = re.sub(r"class CarteraCreditoCarga\(models\.Model\):.*", new_model, content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Model updated.")
