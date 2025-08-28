from flask import Flask, request, jsonify
from datetime import datetime
from functions import *
import os
import json

app = Flask(__name__)

# Učitavanje service JSON iz environment variable
GSHEET_SERVICE_JSON = os.getenv("GSHEET_SERVICE_JSON")
if not GSHEET_SERVICE_JSON:
    raise ValueError("Environment variable 'GSHEET_SERVICE_JSON' nije postavljena!")

service_info = json.loads(GSHEET_SERVICE_JSON)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zSM2URKs4gylIT-uz2NS3B_t3EJ4bVc84LtC1hd9Q1E"

gc, sh, input_wks, output_wks, status_wks = init_gsheet(service_info, SHEET_URL)

@app.route("/process", methods=["POST"])
def process():
    try:
        ocisti_pripremu(output_wks)

        row, split_values, signal_link = main_filtriranje(gc, input_wks, output_wks)
        prva_vrednost_grupa_1, treca_vrednost_grupa_2, cetvrta_vrednost_grupa_2, treca_vrednost_grupa_3 = obradi_i_upisi_grupe(input_wks, output_wks, 5)
        splitovane, poslednjih_8 = ucitaj_i_splituj_vrednosti(input_wks, 5)
        values_DG, values_DH, integral_DQ, rezultat_dm26 = obradi_i_upisi_signale(row, output_wks, splitovane, gc)
        DN_niz = izracunaj_i_upisi_DN_i_DO(output_wks, values_DG, values_DH, poslednjih_8, rezultat_dm26)
        upisi_DR_DS_i_DT(output_wks, values_DH, DN_niz)
        upisi_DU(output_wks, DN_niz, prva_vrednost_grupa_1)
        upisi_DV(output_wks, DN_niz, treca_vrednost_grupa_2)
        upisi_DW(output_wks, DN_niz, integral_DQ)
        upisi_DX(output_wks, DN_niz, integral_DQ)
        upisi_DY(output_wks, DN_niz, cetvrta_vrednost_grupa_2)
        upisi_SLC_tekst_u_DZ(output_wks, DN_niz, treca_vrednost_grupa_3)

        status_wks.update_value('A2', 'OFF')
        status_wks.update_value('B2', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return jsonify({"message": "✅ Obrada završena"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
