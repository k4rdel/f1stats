import httpx

async def winning_percentage(driver_id: str) -> float:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results/1.json"
        )
        response2 = await client.get(
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
            response = await client.get(
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}/results/1.json?limit=100&offset={offset}"
            )
            data = response.json()["MRData"]["RaceTable"]["Races"]
            if not data:
                break
            for x in range(len(data)):
                try: 
                    if data[x]["Results"][0]["grid"] == "1" and data[x]["Results"][0]["FastestLap"]["rank"] == "1":
                        hatTriks += 1
                except KeyError:
                    continue
            
            offset += 100
            
            if offset >= int(response.json()["MRData"]["total"]):
                break
        return hatTriks