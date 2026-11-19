from app.services.mock_data import ASSETS, INCIDENTS

def get_assets(provider=None, environment=None, resource_type=None):
    results = ASSETS
    if provider:
        results = [a for a in results if a["provider"] == provider]
    if environment:
        results = [a for a in results if a["environment"] == environment]
    if resource_type:
        results = [a for a in results if a["resource_type"].lower() == resource_type.lower()]
    return results

def get_asset_by_id(asset_id: str):
    return next((a for a in ASSETS if a["id"] == asset_id), None)

def get_incidents_for_asset(asset_id: str):
    return [i for i in INCIDENTS if asset_id in i["affected_asset_ids"]]
