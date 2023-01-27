from geopy.geocoders import Nominatim


# TODO: Criar uma dag para ser executada manualmente para atualizar a lat. e long. de espeficos cnes_id
def get_location(cep, endereco):
    geolocator = Nominatim(user_agent="location_of_builds_with_cnes")

    location_by_endereco = geolocator.geocode(endereco)
    if location_by_endereco:
        return location_by_endereco.latitude, location_by_endereco.longitude

    location_by_cep = geolocator.geocode(cep)
    if location_by_cep:
        return location_by_cep.latitude, location_by_cep.longitude

    return None, None


def updated_lat_and_lon_columns(df):
    # TODO: Criar uma coluna endereco_precisao(char)[ruim{lat. e long.}, proxima{rua}, boa{numero e rua}]
    endereco = " ".join(df[
                            ['numero_estabelecimento', 'endereco_estabelecimento']
                        ].values[0]).replace("None", "")
    cep = df['codigo_cep_estabelecimento'].values[0]

    # TODO: Criar uma planilha onde seria colocado os cnes_id que não possuem boas info de localização
    if cep or endereco:
        latitude, longitude = get_location(cep, endereco)
        df[
            ['latitude_estabelecimento_decimo_grau',
             'longitude_estabelecimento_decimo_grau']
        ] = latitude, longitude

    return df
