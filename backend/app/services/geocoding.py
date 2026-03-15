import httpx
from typing import Optional

async def reverse_geocod(lat: float, lon: float) -> Optional[str]:
    """
    Определяет тип места по координатам с помощью Nominatim API.
    Возвращает строку: 'home', 'work', 'gym', 'cafe', 'other' или None.  
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 18,
        "addressdetails": 1
    }
    header ={
        "User-Agent": "JarvisApp/1.0 (yarulin.g@mail.ru)"
    }
    async with httpx.AsyncClient() as client:
        try: 
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            if "adderess" in data:
                address = data["address"]
                if "amenity" in address:
                    amenity = address["amenity"].lower()
                    if "gym" in amenity or "fitness" in amenity:
                        return "gym"
                    if "cafe" in amenity or "restaurant" in amenity:
                        return "cafe"
                if "shop" in address:
                    return "shop"
                if "office" in address or "company" in address:
                    return "work"
                if "residentinal" in address or "house" in address:
                    return "home"     
            return "other"
        except Exception:
            return None            