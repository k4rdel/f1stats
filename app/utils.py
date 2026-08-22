import asyncio
from fastapi import HTTPException
import httpx

def handleNotFoundRaces(response, offset):
    if response.json()["MRData"]["RaceTable"]["Races"] == [] and offset == 0:
        raise HTTPException(status_code=404, detail="Races not found")

async def get_with_retry(client, url, max_retries=3):
    for attempt in range(max_retries):
        response = await client.get(url)
        if response.status_code == 429:
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
            continue
        return response
    return response

async def winning_percentage(driver_id: str) -> float:
    async with httpx.AsyncClient() as client:
        response = await get_with_retry(
            client,
            f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results/1.json"
        )
        response2 = await get_with_retry(
            client,
            f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results.json"
        )
        
        winnedRaces = int(response.json()["MRData"]["total"])
        allRaces = int(response2.json()["MRData"]["total"])
        if winnedRaces is None or allRaces is None:
            return 0
        return round(((winnedRaces / allRaces) * 100), 2)
    
async def howManyHatTricks(driver_id: str) -> int:
    hatTriks = 0
    offset = 0
    async with httpx.AsyncClient() as client:
        while True:
            response = await get_with_retry(
                client,
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results/1.json?limit=100&offset={offset}"
            )
            handleNotFoundRaces(response, offset)
            
            data = response.json()["MRData"]["RaceTable"]["Races"]
            if not data:
                break
            for x in range(len(data)):
                try: 
                    if data[x]["Results"][0]["grid"] == "1" and data[x]["Results"][0]["FastestLap"]["rank"] == "1":
                        hatTriks += 1
                except (KeyError, IndexError):
                    continue
            
            offset += 100
            
            if offset >= int(response.json()["MRData"]["total"]):
                break
        return hatTriks

async def howManyPoles(driver_id: str) -> int:
    poles = 0
    offset = 0
    async with httpx.AsyncClient() as client:
        while True:
            response = await get_with_retry(
                client,
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results.json?limit=100&offset={offset}"
            )
            handleNotFoundRaces(response, offset)
            
            data = response.json()["MRData"]["RaceTable"]["Races"]
            if not data:
                break
            for x in range(len(data)):
                try:
                    if data[x]["Results"][0]["grid"] == "1":
                        poles += 1
                except (KeyError, IndexError):
                    continue
            
            offset += 100
            
            if offset >= int(response.json()["MRData"]["total"]):
                break
        return poles
    
async def howManyPodiums(driver_id: str) -> int:
    podiums = 0
    async with httpx.AsyncClient() as client:
        for endPosition in range(1, 4):
            response = await get_with_retry(
                client,
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results/{endPosition}.json?limit=1"
            )
            
            podiums += int(response.json()["MRData"]["total"])
        return podiums

async def averagePositions(driver_id: str) -> tuple[float, float]:
    start_positions_sum = 0 
    end_positions_sum = 0
    valid_races_count = 0
    offset = 0
    async with httpx.AsyncClient() as client:
        while True:
            response = await get_with_retry(
                client,
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results.json?limit=100&offset={offset}"
            )
            handleNotFoundRaces(response, offset)
            
            data = response.json()["MRData"]["RaceTable"]["Races"]
            
            if not data:
                break
            
            all_races = int(response.json()["MRData"]["total"])
            
            for race in data:
                try:
                    start_positions_sum += int(race["Results"][0]["grid"])
                    end_positions_sum += int(race["Results"][0]["position"])
                    valid_races_count += 1 
                except (KeyError, IndexError):
                    continue
            
            offset += 100
            
            if offset >= all_races:
                break
            
    if valid_races_count == 0:
        return 0.0, 0.0
    return round((start_positions_sum / valid_races_count), 2), round((end_positions_sum / valid_races_count), 2)