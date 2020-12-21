from db.user_db import UserDB
from db.user_db import database_users
from db.user_db import update_user, post_user, get_user
from models.user_models import UserIn
from db.movement_db import MovementInDB
from db.movement_db import save_movement
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.movement_models import MovementOut, get_movements, add_movement


api = FastAPI()

origins = [
     "http://localhost", 
     "http://localhost:8080",
     "http://app-misfinanzas.herokuapp.com",
     "https://app-misfinanzas.herokuapp.com"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# página de inicio
@api.get("/")
def inicio():
    #inicio de la aplicacion, petición de usuario
    return {"Pagina de Inicio": "Mision TIC 2022 - Mis Finanzas"}

@api.get("/users/")
async def users():
    return {"message": database_users}

# mostrar usuario
@api.get("/users/{username}")
async def display_user(username: str):
    user_in_db = get_user(username)
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    user_out = UserIn(**user_in_db.dict())
    return user_out

# crear usuario
@api.post("/users/")
async def create_user(user_in: UserDB):
    database_users[user_in.username] = user_in
    return user_in

# autenticar usuario
@api.post("/users/auth/")
async def auth_user(user_in: UserIn):
    user_in_db = get_user(user_in.username)
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    if user_in_db.password != user_in.password:
        raise HTTPException(status_code=403, detail="Error de autenticacion")
    return  {"Autenticado": True}


# mostrar balance del usuario
@api.get("/users/{username}/balance")
async def display_user_balance(username: str):
    user_in_db = get_user(username)
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    user_out = UserIn(**user_in_db.dict())
    return user_out.budget





@api.post("/movimiento/")
async def agregar_movimiento(movement: MovementOut):
    creado = add_movement(movement)
    if creado:
        return {"mensaje": "Movimiento generado"}
    else:
        raise HTTPException(status_code=400, detail="Lo siento, la id del movimiento esta ya creada")


@api.get("/movimientos/ver")
async def obtener_movimientos(username: str):
    movimientos = get_movements(username)
    return movimientos


# movimiento de usuario
@api.put("/users/{username}/movement/")
async def make_movement(movement_in: MovementOut):
    
    user_in_db = get_user(movement_in.username)

    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")

    if movement_in.concept == 'outcome' and user_in_db.budget <= movement_in.amount: 
        raise HTTPException(status_code=400, detail="El gasto ingresado supera su balance actual de ahorro")

    if movement_in.concept == 'outcome':
        user_in_db.budget = user_in_db.budget - movement_in.amount
    else:
        user_in_db.budget = user_in_db.budget + movement_in.amount

    update_user(user_in_db)
    movement_in_db = MovementInDB(**movement_in.dict(), budget = user_in_db.budget)
    movement_in_db = save_movement(movement_in_db)

    movement_out = MovementOut(**movement_in_db.dict())

    return  movement_out