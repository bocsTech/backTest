# import pymongo

# client = pymongo.MongoClient("mongodb://localhost:27017/")

# mydb = client["mydatabase"]

# locales = mydb["locales"]



# from secrets import choice
# from faker import Faker
# import random

# comida = ["Pasta", "Pizza", "Hamburguesa", "Ensalada", "Sushi", "Burrito", "Tacos", "Agua", "Cerveza", "Refresco", "Jugo", "Cafe"]
# precios = {
#     "Pasta": 20000,
#     "Pizza": 30000,
#     "Hamburguesa": 30000,
#     "Ensalada": 20000,
#     "Sushi": 30000,
#     "Burrito": 22000,
#     "Tacos": 25000,
#     "Agua": 5000,
#     "Cerveza": 7000,
#     "Refresco": 5000,
#     "Jugo": 6000,
#     "Cafe": 3000
# }


# fake = Faker("es_CO")
# Faker.seed(10)

# def create_fake_purchase():
#     falso = Faker("es_CO")
#     usuarios = []
#     rand = random.randint(15,40)
#     for _ in range(rand):
#         usuario = { 
#             "date": falso.date_time_this_year(),
#             "client": falso.unique.name(),
#             "food": [choice(comida) for _ in range(fake.random_int(min=1, max=5))]
#             }
#         usuario["amount"] = sum(precios[i] for i in usuario["food"])
#         usuarios.append(usuario)
#     return usuarios


# values = []
# for _ in range(4):
#     cliente = {
#     "name": fake.unique.company(),
#     "hash": fake.unique.sha256(),
#     "address": fake.unique.address(),
#     "email": fake.unique.email(),
#     "phone": fake.unique.phone_number(),
#     "purchases": create_fake_purchase(),   
#     }
#     values.append(cliente)



