import datetime

from fastapi import APIRouter

from src.api.dependencies import AlertQueryServiceDependency
from src.models.alert_response import AlertResponse
from src.models.city_name import CityName

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def get_all_alerts(alert_query_service: AlertQueryServiceDependency) -> list[AlertResponse]:
    return alert_query_service.get_all()


@router.get("/by-date")
def get_alerts_by_date(date: datetime.date, alert_query_service: AlertQueryServiceDependency) -> list[AlertResponse]:
    return alert_query_service.get_by_date(date)


@router.get("/by-city")
def get_alerts_by_city(city: CityName, alert_query_service: AlertQueryServiceDependency) -> list[AlertResponse]:
    return alert_query_service.get_by_city(city)
