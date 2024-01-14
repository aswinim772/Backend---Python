from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter,Depends,HTTPException,Path
from typing import Annotated
from models import Results
from database import SessionLocal
import models
from starlette import status
from pydantic import BaseModel,Field
from starlette.responses import JSONResponse

router = APIRouter(
    prefix='/results',
    tags=['results']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session,Depends(get_db)]


class ResultsRequest(BaseModel):

    name : str = Field(min_length=3)
    address : str = Field(min_length=3,max_length=100)
    city : str
    country: str
    pincode:int
    sat_score : int = Field(gt=-1,lt=101)

@router.post('/insert_data',status_code=status.HTTP_201_CREATED)
def create_todo(db:db_dependancy,new_data:ResultsRequest):

    try:

        if new_data.sat_score >= 30:
            passed = "pass"
        else:
            passed ="fail"

        if len(str(new_data.pincode))!= 6:
            return JSONResponse({"detail":'INVALID PINCODE'},status_code=422)

        results_model=Results(
            name = new_data.name,
            address = new_data.address,
            city = new_data.city,
            country = new_data.country,
            pincode = new_data.pincode,
            sat_score = new_data.sat_score,
            passed = passed
        )

        db.add(results_model)
        db.commit()

        return {"message":"RESULTS ADDED SUCESSFULLY","status_code":status.HTTP_201_CREATED}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

    finally:
        db.close()



@router.get('/view_all_Data',status_code=status.HTTP_200_OK)
def read_all_results(db:db_dependancy):

    try:
        results_model = db.query(Results).all()

        if not results_model:
            return JSONResponse({"detail":'RESULTS NOT FOUND'},status_code=404)

        return {"message":"SUCESSFULL","data":results_model,"status_code":status.HTTP_200_OK}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

    finally:
        db.close()

@router.get('get_rank/{name}')
def get_rank(db:db_dependancy,name:str =Path):

    try:
        results_model = db.query(Results).filter(func.lower(Results.name) == func.lower(name)).first()

        if results_model is None:
            return JSONResponse({"detail":'RESULT NOT FOUND'},status_code=404)

        rank = db.query(Results).distinct().filter(Results.sat_score > results_model.sat_score).count()+1

        if rank == 0:
            rank =1
        return {"name": name, "rank": rank}
        # print(len(resultsl))
        # return resultsl

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

    finally:
        db.close()

@router.put('/update_score/{name}')
def update_todo(db:db_dependancy,updated_score:int,name:str = Path()):

    try:

        results_model = db.query(Results).filter(func.lower(Results.name) == func.lower(name)).first()

        if updated_score not in range(0,101):
            return JSONResponse({"detail":'INVALID SCORE'},status_code=422)

        if results_model is None:
            return JSONResponse({"detail":'RESULT NOT FOUND'},status_code=404)

        if updated_score >= 30:
            passed = "pass"
        else:
            passed ="fail"

        results_model.sat_score = updated_score
        results_model.passed = passed

        db.add(results_model)
        db.commit()

        return {"message":"SCORE UPDATED SUCESSFULLY","status_code":status.HTTP_204_NO_CONTENT}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

    finally:
        db.close()


@router.delete('/{name}')
def delete_todo(db:db_dependancy,name:str = Path):

    try:
        results_model = db.query(Results).filter(func.lower(Results.name) == func.lower(name)).first()

        if results_model is None:
            return JSONResponse({"detail":'RESULT NOT FOUND'},status_code=404)

        db.query(Results).filter(Results.name == name).delete()
        db.commit()

        return {"message":"DATA DELETED SUCESSFULLY","status_code":status.HTTP_204_NO_CONTENT}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

    finally:
        db.close()
