from fastapi import APIRouter, Depends
from app.deps import get_settings, get_inspection_service
from app.schemas import TriggerRequest, TriggerResponse, InspectionResult

router = APIRouter()


@router.post("/trigger", response_model=TriggerResponse)
def trigger(req: TriggerRequest = TriggerRequest(), settings=Depends(get_settings)):
    from app.services.trigger import TriggerService
    svc = TriggerService()
    ts = svc.software_trigger()
    return TriggerResponse(triggered=True, message=f"Triggered at {ts}")


@router.post("/inspect", response_model=InspectionResult)
def run_inspection(
    settings=Depends(get_settings),
    inspection_service=Depends(get_inspection_service),
):
    return inspection_service.run_inspection(settings)
