from fastapi import FastAPI, HTTPException, Path, Body
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Path
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
    travelType: str

class TourGuide(BaseModel):
    travelType: str    

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
    {"NIKID": "101", "Name": "Ale", "Email": "aleale@gmail.com", "Phone": "08123456789", "Address": "Bandung", "CreditCardNumber": "305123456"},
    {"NIKID": "102", "Name": "Leo", "Email": "leoamalia@yahoo.co.id", "Phone": "08789012345", "Address": "Gianyar", "CreditCardNumber": "305123457"},
    {"NIKID": "103", "Name": "Lea", "Email": "leavilia.jet@gmail.com", "Phone": "08134567890", "Address": "Yogyakarta", "CreditCardNumber": "305123458"},
    {"NIKID": "104", "Name": "Satoru", "Email": "satorusatria@gmail.com", "Phone": "08778901234", "Address": "Surabaya", "CreditCardNumber": "305123459"},
    {"NIKID": "105", "Name": "Suguru", "Email": "suguruarianto@student.telkomuniversity.ac.id", "Phone": "08156789012", "Address": "Jakarta Selatan", "CreditCardNumber": "305123460"},
]

reservations = [
    {"ReservationID": "1", "NIKID": "101", "RoomID": "1", "CheckInDate": "2024-10-27", "CheckOutDate": "2024-10-28", "TotalAmount": 1000000, "idPenyewaanMobil": "001"},
    {"ReservationID": "2", "NIKID": "102", "RoomID": "2", "CheckInDate": "2024-10-31", "CheckOutDate": "2024-11-01", "TotalAmount": 1000000, "idPenyewaanMobil": "002"},
    {"ReservationID": "3", "NIKID": "103", "RoomID": "3", "CheckInDate": "2024-11-01", "CheckOutDate": "2024-11-03", "TotalAmount": 4000000, "idPenyewaanMobil": "003"},
    {"ReservationID": "4", "NIKID": "104", "RoomID": "4", "CheckInDate": "2024-11-01", "CheckOutDate": "2024-11-02", "TotalAmount": 2000000, "idPenyewaanMobil": "004"},
    {"ReservationID": "5", "NIKID": "105", "RoomID": "5", "CheckInDate": "2024-11-02", "CheckOutDate": "2024-11-04", "TotalAmount": 6000000, "idPenyewaanMobil": "005"},
]

reviews = [
    {"ReviewID": "1", "ReservationID": "1", "Rating": 5, "Comment": "Pelayanan yang sangat baik dan kamar nyaman.", "InputDate": "2024-11-28", "travelType": "Business"},
    {"ReviewID": "2", "ReservationID": "2", "Rating": 4, "Comment": "Lokasi bagus, tapi kebersihan bisa ditingkatkan.", "InputDate": "2024-11-01", "travelType": "Others"},
    {"ReviewID": "3", "ReservationID": "3", "Rating": 5, "Comment": "Saya benar-benar menyukai penginapanku! Semuanya sempurna.", "InputDate": "2024-11-03", "travelType": "Education"},
    {"ReviewID": "4", "ReservationID": "4", "Rating": 4, "Comment": "Staf yang ramah dan fasilitas yang bagus.", "InputDate": "2024-11-02", "travelType": "Holiday"},
    {"ReviewID": "5", "ReservationID": "5", "Rating": 3, "Comment": "Pengalaman menginap yang lumayan, tapi Wi-Fi tidak stabil.", "InputDate": "2024-11-04", "travelType": "Business"},
]

rooms = [
    {"RoomID": "1", "RoomNumber": "100", "RoomType": "Standard Room", "Rate": 1000000, "Availability": "Occupied", "Insurance": "AA04"},
    {"RoomID": "2", "RoomNumber": "101", "RoomType": "Standard Room", "Rate": 1000000, "Availability": "Occupied", "Insurance": "AA04"},
    {"RoomID": "3", "RoomNumber": "200", "RoomType": "Superior Room", "Rate": 2000000, "Availability": "Empty", "Insurance": "AA04"},
    {"RoomID": "4", "RoomNumber": "201", "RoomType": "Superior Room", "Rate": 2000000, "Availability": "Maintenance", "Insurance": "AA04"},
    {"RoomID": "5", "RoomNumber": "300", "RoomType": "Kings Room", "Rate": 3000000, "Availability": "Occupied", "Insurance": "AA04"},
]

# Utility functions to get the index of items
def get_index(data, key, value):
    for index, item in enumerate(data):
        if item[key] == value:
            return index
    return None

# CRUD operations for Billings

async def get_bank_from_web():
    url = "https://jumantaradev.my.id/api/hotel"  # endpoint kelompok bank
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']['data']
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from the bank API.")

class Billing(BaseModel):
    id: int
    jenis: str
    name: str
    total: str

@app.get("/billings", response_model=List[Billing])
async def get_billings():
    billings = await get_bank_from_web()
    return billings

@app.get("/billings/{bill_id}", response_model=Optional[Billing])
async def get_billing(bill_id: int):
    billings = await get_bank_from_web()  # Fetch billings
    for billing in billings:
        if billing['id'] == bill_id:
            return Billing(**billing)
    raise HTTPException(status_code=404, detail="Billing not found")

@app.post("/billings", response_model=Billing)
async def create_billing(billing: Billing):
    # Logic to create a new billing
    return billing

@app.put("/billings/{bill_id}", response_model=Billing)
async def update_billing(bill_id: int, billing: Billing):
    # Logic to update billing with given bill_id
    return billing

@app.delete("/billings/{bill_id}")
async def delete_billing(bill_id: int):
    billings = await get_bank_from_web()  # Fetch billings
    for billing in billings:
        if billing['id'] == bill_id:
            billings.pop(billing)
            return {"message": "Billing deleted successfully"}
    raise HTTPException(status_code=404, detail="Billing not found")

# CRUD operations for Guests

# --------------------
# Get Data Guest All
# --------------------
async def get_penduduk_from_web():
    url = "https://api-government.onrender.com/penduduk"  #endpoint kelompok Government
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil Government Data.")

class Government(BaseModel):
    nik: int
    nama: str
    kota: str

@app.get("/penduduk", response_model=List[Government])
async def get_penduduk():
    data_government = await get_penduduk_from_web()
    return data_government

# --------------------
# Get Data Guest Individual
# --------------------
@app.get("/penduduk/{penduduk_id}", response_model=Optional[Government])
async def get_penduduk(guest_id: int):
    guests = await get_penduduk_from_web() 
    for guest in guests:
        if guest['nik'] == guest_id:
            return Government(**guest)
    raise HTTPException(status_code=404, detail="Penduduk not found")

# --------------------
# Check Data Get Guest
# --------------------
@app.get("/guests", response_model=List[Guest])
def get_guests():
    return guests

# --------------------
# Post Data Guest
# --------------------
@app.post("/guests")
def create_guest(guest: Guest):
    guests.append(guest)
    return guest

# --------------------
# Put Data Guest
# --------------------
@app.put("/guests/{nik}")
def update_guest(nik: str, guest: Guest):
    index = get_index(guests, 'NIKID', nik)
    if index is not None:
        guests[index] = guest
        return guests[index]
    raise HTTPException(status_code=404, detail="Guest not found")

# --------------------
# Delete Data Guest
# --------------------
@app.delete("/guests/{nik}")
def delete_guest(nik: str):
    index = get_index(guests, 'NIKID', nik)
    if index is not None:
        guests.pop(index)
        return {"message": "Guest deleted successfully"}
    raise HTTPException(status_code=404, detail="Guest not found")

# --------------------
# Get Data Kartu Kredit All
# --------------------
async def get_kartu_from_web():
    url = "https://jumantaradev.my.id/api/hotel"  #endpoint kelompok kartu kredit
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']['data']
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil Kartu Kredit.")

class Bank(BaseModel):
    id: int
    name: str 

@app.get("/kartu_kredit", response_model=List[Bank])
async def get_kartu():
    data_kartu = await get_kartu_from_web()
    return data_kartu

# --------------------
# Get Data Kartu Kredit Individual
# --------------------

@app.get("/kartu_kredit/{kartukredit}", response_model=Optional[Bank])
async def get_kartu(kartu_id: int):
    cards = await get_kartu_from_web() 
    for card in cards:
        if card['id'] == kartu_id:
            return Bank(**card)
    raise HTTPException(status_code=404, detail="Kartu not found")


# CRUD operations for Reservations
async def get_sewa_from_web():
    url = "https://rental-mobil-api.onrender.com/penyewaan"  #endpoint kelompok tour guide
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil Mobil.")

class Penyewaan(BaseModel):
    id_penyewaan: str

@app.get("/penyewaan", response_model=List[Penyewaan])
async def get_penyewaan():
    data_penyewaan = await get_sewa_from_web()
    return data_penyewaan

@app.get("/penyewaan/{reservation_id}", response_model=Optional[Penyewaan])
async def get_sewa(reservation_id: str):
    reservations = await get_sewa_from_web()  # Fetch billings
    for reservation in reservations:
        if reservation['id_penyewaan'] == reservation_id:
            return Penyewaan(**reservation)
    raise HTTPException(status_code=404, detail="Reservation not found")
    
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

@app.delete("/reservations/{reservation_id}", response_model=dict)
def delete_reservation(reservation_id: str = Path(..., title="Reservation ID", description="The ID of the review to delete")):
    index = get_index(reservations, 'ReservationID', reservation_id)
    if index is not None:
        deleted_reservation = reservations.pop(index)
        return {"message": "Review deleted successfully", "deleted_review": deleted_reservation}
    raise HTTPException(status_code=404, detail="Review not found")

# CRUD operations for Reviews
@app.get("/reviews", response_model=List[Review])
def get_reviews():
    return reviews

@app.get("/reviews/{review_id}", response_model=Optional[Review])
def get_review(review_id: str = Path(..., title="Review ID", description="The ID of the review to retrieve")):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        return reviews[index]
    raise HTTPException(status_code=404, detail="Review not found")

@app.post("/reviews", response_model=Review)
def create_review(review: Review = Body(..., embed=True)):
    reviews.append(review.dict())
    return review

@app.put("/reviews/{review_id}", response_model=Review)
def update_review(review_id: str = Path(..., title="Review ID", description="The ID of the review to update"), review: Review = Body(..., embed=True)):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        reviews[index] = review.dict()
        return review
    raise HTTPException(status_code=404, detail="Review not found")

@app.delete("/reviews/{review_id}", response_model=dict)
def delete_review(review_id: str = Path(..., title="Review ID", description="The ID of the review to delete")):
    index = get_index(reviews, 'ReviewID', review_id)
    if index is not None:
        deleted_review = reviews.pop(index)
        return {"message": "Review deleted successfully", "deleted_review": deleted_review}
    raise HTTPException(status_code=404, detail="Review not found")

# CRUD operations for Rooms
async def get_insurance_endpoint():
    url = "https://eai-fastapi.onrender.com/asuransi"  #endpoint kelompok asuransi
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil insurance.")

async def get_insurance_byID(id_asuransi: str):
    url = f"https://eai-fastapi.onrender.com/asuransi/{id_asuransi}"  #endpoint kelompok asuransi
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Gagal mengambil insurance.")


class insurance(BaseModel):
    id_asuransi: str
    jenis_asuransi: str
    objek: str

@app.get("/insurance", response_model=List[insurance])
async def get_insurance():
    data_insurance = await get_insurance_endpoint()
    return data_insurance

@app.get("/insurance/{id_asuransi}", response_model=Optional[insurance])
async def get_insurance(id_asuransi: str):
    insurances = await get_insurance_endpoint()  # Fetch billings
    for insur in insurances:
        if insur['id_asuransi'] == id_asuransi:
            return insurance(**insur)
    raise HTTPException(status_code=404, detail="Billing not found")

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
    url = "https://tour-guide-ks4n.onrender.com/tourguide"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Gagal mengambil Tour Guide.")

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
