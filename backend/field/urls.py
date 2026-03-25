from django.urls import path
from field.views import (
    FieldDataView, SavePolygon, GetCoordView, AWDreport, CarbonCredit,
    PestPrediction, HealthScore, WeatherView, FieldLogView, FieldAlertView,
    EEAnalysisView, PestReport, SoilAdviceView, BulkMarkAlertsReadView
)
from field.views.irrigation import IrrigationScheduleView, IrrigationLogView
from field.views.yield_prediction import YieldPredictionView

urlpatterns = [
    path('data', FieldDataView.as_view(), name='fieldList'),
    path('data/<int:pk>', FieldDataView.as_view(), name='fieldDetail'),
    path('ee', EEAnalysisView.as_view(), name='fieldAnalysis'),
    path('set_polygon', SavePolygon.as_view(), name='savePolygon'),
    path('coord', GetCoordView.as_view(), name='getCoord'),
    path('awd', AWDreport.as_view(), name='AWDreport'),
    path('cc', CarbonCredit.as_view(), name='CarbonCredit'),
    path('pestpredict', PestPrediction.as_view(), name='PestPrediction'),
    path('pest/report', PestReport.as_view(), name='PestReport'),
    path('healthscore', HealthScore.as_view(), name='HealthScore'),
    path('weather', WeatherView.as_view(), name='weather'),
    # FieldLog API
    path('logs', FieldLogView.as_view(), name='fieldLogs'),
    path('logs/<int:pk>', FieldLogView.as_view(), name='fieldLogDetail'),
    # FieldAlert API
    path('alerts', FieldAlertView.as_view(), name='fieldAlerts'),
    path('alerts/all', FieldAlertView.as_view(), kwargs={'pk': 'all'}, name='fieldAlertBulkRead'),
    path('alerts/mark-all-read', BulkMarkAlertsReadView.as_view(), name='fieldAlertBulkMarkRead'),
    path('alerts/<int:pk>', FieldAlertView.as_view(), name='fieldAlertDetail'),
    # Soil Advice API
    path('soil-advice', SoilAdviceView.as_view(), name='soilAdvice'),
    # Irrigation API
    path('irrigation-schedule', IrrigationScheduleView.as_view(), name='irrigationSchedule'),
    path('irrigation-logs', IrrigationLogView.as_view(), name='irrigationLogs'),
    path('irrigation-logs/<int:pk>', IrrigationLogView.as_view(), name='irrigationLogDetail'),
    # Yield Prediction API
    path('yield-prediction', YieldPredictionView.as_view(), name='yieldPrediction'),
]