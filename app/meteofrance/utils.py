from datetime import datetime
from typing import List

from app.meteofrance.schemas import MeteoFranceInfrahoraireMessage


def consume_meteofrance_message(message: dict) -> List[MeteoFranceInfrahoraireMessage]:
    """
    Consume base meteofrance message to MeteoFranceInfrahoraireMessage model.

    :param message:
    :return:
    """
    data_list = []
    for data in message:
       data_list.append(MeteoFranceInfrahoraireMessage(
            lat=data.get("lat"),
            lon=data.get("lon"),
            geo_id_insee=data.get("geo_id_insee"),
            reference_time=datetime.fromisoformat(data.get("reference_time")),
            insert_time=datetime.fromisoformat(data.get("insert_time")),
            validity_time=datetime.fromisoformat(data.get("validity_time")),
            t=data.get("t"),
            td=data.get("td"),
            u=data.get("u"),
            dd=data.get("dd"),
            ff=data.get("ff"),
            dxi10=data.get("dxi10"),
            fxi10=data.get("fxi10"),
            rr_per=data.get("rr_per"),
            t_10=data.get("t_10"),
            t_20=data.get("t_20"),
            t_50=data.get("t_50"),
            t_100=data.get("t_100"),
            vv=data.get("vv"),
            etat_sol=data.get("etat_sol"),
            sss=data.get("sss"),
            insolh=data.get("insolh"),
            ray_glo01=data.get("ray_glo01"),
            pres=data.get("pres"),
            pmer=data.get("pmer")
        )
       )
    return data_list