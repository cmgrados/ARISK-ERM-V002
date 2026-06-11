from django.contrib import admin
from .models import (
    LiqBalanceUpload, LiqBalanceDetail, LiqSavingsUpload, LiqSavingsAccount,
    LiqTermDepositUpload, LiqTermDeposit, LiqContributor, LiqFundingLine,
    LiqInvestment, LiqAvailableFund, LiqPortfolioDetail, LiqAccountMapping,
    LiqTimeBand, LiqMonthlyPosition, LiqMonthlyIndicator, LiqGapReport,
    LiqGapDetail, LiqConcentrationReport, LiqStressScenario, LiqStressRun,
    LiqStressResult, LiqLimit, LiqAlert, LiqBreach, LiqContingencyPlan,
    LiqContingencyActivation, LiqContingencyAction, LiqReport, LiqApproval,
    LiqAuditLog, LiqLaRConfig, LiqLaRResult
)

@admin.register(LiqBalanceUpload)
class LiqBalanceUploadAdmin(admin.ModelAdmin):
    list_display = ('period', 'status', 'user', 'created_at')

@admin.register(LiqSavingsUpload)
class LiqSavingsUploadAdmin(admin.ModelAdmin):
    list_display = ('period', 'status', 'created_at')

@admin.register(LiqTermDepositUpload)
class LiqTermDepositUploadAdmin(admin.ModelAdmin):
    list_display = ('period', 'status', 'created_at')

admin.site.register(LiqBalanceDetail)
admin.site.register(LiqSavingsAccount)
admin.site.register(LiqTermDeposit)
admin.site.register(LiqContributor)
admin.site.register(LiqFundingLine)
admin.site.register(LiqInvestment)
admin.site.register(LiqAvailableFund)
admin.site.register(LiqPortfolioDetail)
admin.site.register(LiqAccountMapping)
admin.site.register(LiqTimeBand)
admin.site.register(LiqMonthlyPosition)
admin.site.register(LiqMonthlyIndicator)
admin.site.register(LiqGapReport)
admin.site.register(LiqGapDetail)
admin.site.register(LiqConcentrationReport)
admin.site.register(LiqStressScenario)
admin.site.register(LiqStressRun)
admin.site.register(LiqStressResult)
admin.site.register(LiqLimit)
admin.site.register(LiqAlert)
admin.site.register(LiqBreach)
admin.site.register(LiqContingencyPlan)
admin.site.register(LiqContingencyActivation)
admin.site.register(LiqContingencyAction)
admin.site.register(LiqReport)
admin.site.register(LiqApproval)
admin.site.register(LiqAuditLog)
admin.site.register(LiqLaRConfig)
admin.site.register(LiqLaRResult)
