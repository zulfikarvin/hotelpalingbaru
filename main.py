from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests

app = FastAPI(
    title="Bandar Hotel API",
    description="API untuk mengelola data hotel",
    docs_url="/",
)

# Define Pydantic models for each table
class Billing(BaseModel):
    BillID: str
    ReservationID: str
    TotalAmount: int
    PaymentStatus: str
    CreditCardNumber: str

class Guest(BaseModel):
    NIKID: str
    Name: str
    Email: str
    Phone: str
    Address: str
    CreditCardNumber: str


class Reservation(BaseModel):
    ReservationID: str
    NIKID: str
    RoomID: str
    CheckInDate: str
    CheckOutDate: str
    TotalAmount: float
    idPenyewaanMobil: str

class Review(BaseModel):
    ReviewID: str
    ReservationID: str
    Rating: int
    Comment: str
    InputDate: str
    TravelType: str

class tourguide(BaseModel):
    TravelType : str    

class Room(BaseModel):
    RoomID: str
    RoomNumber: str
    RoomType: str
    Rate: int
    Availability: str
    Insurance: str

# Dummy data
billings = [
    {"BillID": "1", "ReservationID": "1", "TotalAmount": 1000000, "PaymentStatus": "Paid", "CreditCardNumber": "1234"},
    {"BillID": "2", "ReservationID": "2", "TotalAmount": 1000000, "PaymentStatus": "Paid", "CreditCardNumber": "5689"},
    {"BillID": "3", "ReservationID": "3", "TotalAmount": 4000000, "PaymentStatus": "Paid", "CreditCardNumber": "1357"},
    {"BillID": "4", "ReservationID": "4", "TotalAmount": 2000000, "PaymentStatus": "Paid", "CreditCardNumber": "2468"},
    {"BillID": "5", "ReservationID": "5", "TotalAmount": 6000000, "PaymentStatus": "Paid", "CreditCardNumber": "1987"},
]

guests = [
    {"NIKID": "101", "Name": "Ale", "Email": "aleale@gmail.com", "Phone": "08123456789", "Address": "Suite 839 Jl. Hayamwuruk No. 89, Berau, KU 39222", "CreditCardNumber": "1234"},
    {"NIKID": "102", "Name": "Leo", "Email": "leoamalia@yahoo.co.id", "Phone": "08789012345", "Address": "Jl. MH. Thamrin No. 24, Sumbawa, KB 22844", "CreditCardNumber": "5689"},
    {"NIKID": "103", "Name": "Lea", "Email": "leavilia.jet@gmail.com", "Phone": "08134567890", "Address": "Jl. Gajahmada No. 50, Jambi, SG 40689", "CreditCardNumber": "1357"},
    {"NIKID": "104", "Name": "Satoru", "Email": "satorusatria@gmail.com", "Phone": "08778901234", "Address": "Jl. Hayamwuruk No. 30, Bitung, SL 21490", "CreditCardNumber": "2468"},
    {"NIKID": "105", "Name": "Suguru", "Email": "suguruarianto@student.telkomuniversity.ac.id", "Phone": "08156789012", "Address": "Jl. Gatot Soebroto No. 70, Toba Samosir, JA 83706", "CreditCardNumber": "1987"},
]

reservations = [
    {"ReservationID": "1", "NIKID": "101", "RoomID": "1", "CheckInDate": "2024-10-27", "CheckOutDate": "2024-10-28", "TotalAmount": 1000000, "idPenyewaanMobil": "001"},
    {"ReservationID": "2", "NIKID": "102", "RoomID": "2", "CheckInDate": "2024-10-31", "CheckOutDate": "2024-11-01", "TotalAmount": 1000000, "idPenyewaanMobil": "002"},
    {"ReservationID": "3", "NIKID": "103", "RoomID": "3", "CheckInDate": "2024-11-01", "CheckOutDate": "2024-11-03", "TotalAmount": 4000000, "idPenyewaanMobil": "003"},
    {"ReservationID": "4", "NIKID": "104", "RoomID": "4", "CheckInDate": "2024-11-01", "CheckOutDate": "2024-11-02", "TotalAmount": 2000000, "idPenyewaanMobil": "004"},
    {"ReservationID": "5", "NIKID": "105", "RoomID": "5", "CheckInDate": "2024-11-02", "CheckOutDate": "2024-11-04", "TotalAmount": 6000000, "idPenyewaanMobil": "005"},
]

reviews = [
    {"ReviewID": "1", "ReservationID": "1", "Rating": 5, "Comment": "Pelayanan yang sangat baik dan kamar nyaman.", "InputDate": "2024-11-28", "TravelType": "Business"},
    {"ReviewID": "2", "ReservationID": "2", "Rating": 4, "Comment": "Lokasi bagus, tapi kebersihan bisa ditingkatkan.", "InputDate": "2024-11-01", "TravelType": "Others"},
    {"ReviewID": "3", "ReservationID": "3", "Rating": 5, "Comment": "Saya benar-benar menyukai penginapanku! Semuanya sempurna.", "InputDate": "2024-11-03", "TravelType": "Education"},
    {"ReviewID": "4", "ReservationID": "4", "Rating": 4, "Comment": "Staf yang ramah dan fasilitas yang bagus.", "InputDate": "2024-11-02", "TravelType": "Holiday"},
    {"ReviewID": "5", "ReservationID": "5", "Rating": 3, "Comment": "Pengalaman menginap yang lumayan, tapi Wi-Fi tidak stabil.", "InputDate": "2024-11-04", "TravelType": "Business"},
]

rooms = [
    {"RoomID": "1", "RoomNumber": "100", "RoomType": "Standard Room", "Rate": 1000000, "Availability": "Occupied", "Insurance": "305"},
    {"RoomID": "2", "RoomNumber": "101", "RoomType": "Standard Room", "Rate": 1000000, "Availability": "Occupied", "Insurance": "306"},
    {"RoomID": "3", "RoomNumber": "200", "RoomType": "Superior Room", "Rate": 2000000, "Availability": "Empty", "Insurance": "307"},
    {"RoomID": "4", "RoomNumber": "201", "RoomType": "Superior Room", "Rate": 2000000, "Availability": "Maintenance", "Insurance": "308"},
    {"RoomID": "5", "RoomNumber": "300", "RoomType": "Kings Room", "Rate": 3000000, "Availability": "Occupied", "Insurance": "309"},
]

# Utility functions to get the index of items
def get_index(data, key, value):
    for index, item in enumerate(data):
        if item[key] == value:
            return index
    return None

# CRUD operations for Billings
@app.get("/billings", response_model=List[Billing])
def get_billings():
    return billings

@app.get("/billings/{bill_id}", response_model=Optional[Billing])
def get_billing(bill_id: str):
    index = get_index(billings, 'BillID', bill_id)
    if index is not None:
        return billings[index]
    raise HTTPException(status_code=404, detail="Billing not found")

@app.post("/billings")
def create_billing(billing: Billing):
    billings.append(billing.dict())
    return {"message": "Billing created successfully"}

@app.put("/billings/{bill_id}")
def update_billing(bill_id: str, billing: Billing):
    index = get_index(billings, 'BillID', bill_id)
    if index is not None:
        billings[index] = billing.dict()
        return {"message": "Billing updated successfully"}
    raise HTTPException(status_code=404, detail="Billing not found")

@app.delete("/billings/{bill_id}")
def delete_billing(bill_id: str):
    index = get_index(billings, 'BillID', bill_id)
    if index is not None:
        billings.pop(index)
        return {"message": "Billing deleted successfully"}
    raise HTTPException(status_code=404, detail="Billing not found")

# CRUD operations for Guests

# --------------------
# Get Data Guest All
# --------------------
async def get_guest_from_web():
    url = "https://api-government.onrender.com/penduduk"  #endpoint kelompok tour guide
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil Tour Guide.")

class Government(BaseModel):
    nik: int
    nama: str
    kota: str

@app.get("/guest", response_model=List[Government])
async def get_guests():
    data_government = await get_guest_from_web()
    return data_government

# --------------------
# Get Data Guest Individual
# --------------------

@app.get("/guests/{nik}", response_model=Optional[Government])
async def get_guests(nik: int):
    data_government = await get_guest_from_web(nik)
    return data_government

# --------------------
# Check Data Get Guest
# --------------------
@app.get("/penduduk", response_model=List[Guest])
def get_guests():
    return guests

# --------------------
# Post Data Guest
# --------------------
@app.post("/guests")
def create_guest(guest: Guest):
    guests.append(guest.dict())
    return {"message": "Guest created successfully"}

# --------------------
# Put Data Guest
# --------------------
@app.put("/guests/{nik_id}")
def update_guest(nik_id: str, guest: Guest):
    index = get_index(guests, 'NIKID', nik_id)
    if index is not None:
        guests[index] = guest.dict()
        return {"message": "Guest updated successfully"}
    raise HTTPException(status_code=404, detail="Guest not found")

# --------------------
# Delete Data Guest
# --------------------
@app.delete("/guests/{nik_id}")
def delete_guest(nik_id: str):
    index = get_index(guests, 'NIKID', nik_id)
    if index is not None:
        guests.pop(index)
        return {"message": "Guest deleted successfully"}
    raise HTTPException(status_code=404, detail="Guest not found")

# --------------------
# Get Data Kartu Kredit All
# --------------------
async def get_kartu_from_web():
    url = "https://api-government.onrender.com/penduduk"  #endpoint kelompok kartu kredit
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil Kartu Kredit.")

class Bank(BaseModel):
    # tolong check ulang ke padlan
    nomorkartu: str 

@app.get("/kartu_kredit", response_model=List[Bank])
async def get_kartu():
    data_kartu = await get_kartu_from_web()
    return data_kartu

# --------------------
# Get Data Kartu Kredit Individual
# --------------------

@app.get("/kartu_kredit/{kartukredit}", response_model=Optional[Government])
async def get_guests(nik: int):
    data_kartu = await get_guest_from_web(kartukredit)
    return data_kartu

# --------------------
# Check Data Get Kartu Kredit
# --------------------
@app.get("/kartu_kredit", response_model=List[Guest])
def get_guests():
    return guests

# --------------------
# Delete Data Kartu Kredit
# --------------------
@app.delete("/kartu_kredit/{kartukredit}")
# check sama padlan juga yang ini
def delete_kartu(kartukredit: str):
    index = get_index(guests, 'CreditCardNumber', kartukredit)
    if index is not None:
        guests.pop(index)
        return {"message": "Kartu Kredit deleted successfully"}
    raise HTTPException(status_code=404, detail="Kartu Kredit not found")

# CRUD operations for Reservations
@app.get("/reservations", response_model=List[Reservation])
def get_reservations():
    return reservations

@app.get("/reservations/{reservation_id}", response_model=Optional[Reservation])
def get_reservation(reservation_id: str):
    index = get_index(reservations, 'ReservationID', reservation_id)
    if index is not None:
        return reservations[index]
    raise HTTPException(status_code=404, detail="Reservation not found")

@app.post("/reservations")
def create_reservation(reservation: Reservation):
    reservations.append(reservation.dict())
    return {"message": "Reservation created successfully"}

@app.put("/reservations/{reservation_id}")
def update_reservation(reservation_id: str, reservation: Reservation):
    index = get_index(reservations, 'ReservationID', reservation_id)
    if index is not None:
        reservations[index] = reservation.dict()
        return {"message": "Reservation updated successfully"}
    raise HTTPException(status_code=404, detail="Reservation not found")

@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: str):
    index = get_index(reservations, 'ReservationID', reservation_id)
    if index is not None:
        reservations.pop(index)
        return {"message": "Reservation deleted successfully"}
    raise HTTPException(status_code=404, detail="Reservation not found")

# CRUD operations for Reviews
@app.get("/reviews", response_model=List[Review])
def get_reviews():
    return reviews
    

@app.get("/reviews/{review_id}", response_model=Optional[Review])
def get_review(review_id: str):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        return reviews[index]
    raise HTTPException(status_code=404, detail="Review not found")

@app.post("/reviews")
def create_review(review: Review):
    reviews.append(review.dict())
    return {"message": "Review created successfully"}

@app.put("/reviews/{review_id}")
def update_review(review_id: str, review: Review):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        reviews[index] = review.dict()
        return {"message": "Review updated successfully"}
    raise HTTPException(status_code=404, detail="Review not found")

@app.delete("/reviews/{review_id}")
def delete_review(review_id: str):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        reviews.pop(index)
        return {"message": "Review deleted successfully"}
    raise HTTPException(status_code=404, detail="Review not found")

@app.get('/tourguide',response_model=List[tourguide])
async def get_tourguide():
    data_tourguide = await get_tourguide_from_web()
    return data_tourguide

# CRUD operations for Rooms
@app.get("/rooms", response_model=List[Room])
def get_rooms():
    return rooms

@app.get("/rooms/{room_id}", response_model=Optional[Room])
def get_room(room_id: str):
    index = get_index(rooms, 'RoomID', room_id)
    if index is not None:
        return rooms[index]
    raise HTTPException(status_code=404, detail="Room not found")

@app.post("/rooms")
def create_room(room: Room):
    rooms.append(room.dict())
    return {"message": "Room created successfully"}

@app.put("/rooms/{room_id}")
def update_room(room_id: str, room: Room):
    index = get_index(rooms, 'RoomID', room_id)
    if index is not None:
        rooms[index] = room.dict()
        return {"message": "Room updated successfully"}
    raise HTTPException(status_code=404, detail="Room not found")

@app.delete("/rooms/{room_id}")
def delete_room(room_id: str):
    index = get_index(rooms, 'RoomID', room_id)
    if index is not None:
        rooms.pop(index)
        return {"message": "Room deleted successfully"}
    raise HTTPException(status_code=404, detail="Room not found")

# Endpoint untuk mengambil data tour guide
@app.get("/tourguide")
def get_tourguide():
    url = "https://tour-guide-ks4n.onrender.com/tourguide/#/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Gagal mengambil Tour Guide.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)