import pandas as pd
from src.dtw_lab.lab1 import calculate_statistic
import src.dtw_lab.lab2 as lab2
from src.dtw_lab.lab1 import encode_categorical_vars

def test_calculate_statistic():
    df = pd.DataFrame({"Charge_Left_Percentage": [39, 60, 30, 30, 41]})
    assert calculate_statistic("mean", df["Charge_Left_Percentage"]) == 40
    assert calculate_statistic("median", df["Charge_Left_Percentage"]) == 39
    assert calculate_statistic("mode", df["Charge_Left_Percentage"]) == 30

def test_encode_categorical_vars_onehot_and_maps():
    df = pd.DataFrame(
        {
            "Manufacturer": ["Duracell", "Energizer", "Duracell"],
            "Battery_Size": ["AA", "AAA", "D"],
            "Discharge_Speed": ["Fast", "Slow", "Medium"],
        }
    )

    out = encode_categorical_vars(df) 

    # Manufacturer -> one hot
    assert "Manufacturer" not in out.columns
    assert "Manufacturer_Duracell" in out.columns
    assert "Manufacturer_Energizer" in out.columns

    # Mappings
    assert out["Battery_Size"].tolist() == [2, 1, 4]          # AA=2, AAA=1, D=4
    assert out["Discharge_Speed"].tolist() == [3, 1, 2]       # Fast=3, Slow=1, Medium=2


def test_encode_categorical_vars_unknown_values_become_nan():
    df = pd.DataFrame(
        {
            "Manufacturer": ["Duracell"],
            "Battery_Size": ["ZZZ"],          # no está en el mapa
            "Discharge_Speed": ["Turbo"],     # no está en el mapa
        }
    )
    out = encode_categorical_vars(df)

    # One hot sigue funcionando
    assert "Manufacturer_Duracell" in out.columns

    # Valores no mapeados -> NaN
    assert pd.isna(out.loc[0, "Battery_Size"])
    assert pd.isna(out.loc[0, "Discharge_Speed"])


def test_get_statistic_mocks_external_dependency(mocker):
    fake_df = pd.DataFrame({"Charge_Left_Percentage": [10, 20, 30]})

    # Mock de la descarga (evita llamada a red)
    mocker.patch("src.dtw_lab.lab2.read_csv_from_google_drive", return_value=fake_df)

    # Evita que clean_data cambie el DF en este test (opcional)
    mocker.patch("src.dtw_lab.lab2.clean_data", side_effect=lambda df: df)

    result = lab2.get_statistic("mean", "Charge_Left_Percentage")
    assert result["value"] == 20.0