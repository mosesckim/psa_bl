import os
import tqdm
import argparse

import pandas as pd

from src.utils import get_preds


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    # add args
    parser.add_argument(
        "-p", "--path_to_data", default="data"
    )
    parser.add_argument(
        "-f", "--csv_filename", default="BDP cleaned full Plant Code.xlsx"
    )
    # parse
    args = parser.parse_args()
    path_to_data = args.path_to_data
    bdp_file = args.csv_filename

    # read in file
    bdp_file_path = os.path.join(path_to_data, bdp_file)
    bl_df = pd.read_excel(bdp_file_path, sheet_name="BDP December cleaned V2")


    # TODO: automate finding these fields instead of hardcoding as below
    # we choose conditional fields with no nulls
    # and fill in fields that have less than 1000 unique values
    # and fewer than 40 percent null

    necessary_fields = ['CONO', 'CustomerNumber', 'PlantCode', 'CargoTypeID',
        'PortofLoadID', 'PortofDischarge',
        'TarriffServiceCodeTMCCarrier', 'Typeofmove']

    # we exclude some "comment" fields such as
    # NotifyPartyExtraText
    unfilled_fields = ['CarrierAlphaCode',
        'BLReleaseLocationID',
        'OnBoardNotationClause', 'ExporterAddressCode', 'OnBoardNotation',
        'DisplayExpressBillClause', 'MethodofTransportation', 'PlaceofReceipt',
        'CountryUltimateDestination', 'CountryCode',
        'Countryoforigindescription', 'LetterofCreditClause',
        'PartiesofTransaction', 'AESConsigneeType',
        'AESShipperAddressCode', 'ReleaseLocID',
        'SEDClauses', 'Pointoforigincode', 'OnBoardClauseCode',
        ]


    res = {}

    for uf_field in tqdm.tqdm(unfilled_fields):
        stats = get_preds(
            bl_df,
            ff_fields=necessary_fields,
            uf_fields=[uf_field]
        )[1]

        acc = stats.accuracy
        cvg = stats["train coverage in val"] #stats.coverage
        null_perc = stats.null_perc  # this only is meaningful if we don't replace nulls


        res[uf_field] = (acc, cvg, null_perc)


    res_df = pd.Series(res).to_frame()

    res_df.loc[:, "accuracy"] = res_df.apply(lambda x: x[0][0], axis=1)
    res_df.loc[:, "train coverage in val"] = res_df.apply(lambda x: x[0][1], axis=1)
    res_df.loc[:, "null_perc"] = res_df.apply(lambda x: x[0][2], axis=1)

    res_df = res_df[["accuracy", "train coverage in val", "null_perc"]]

    res_df.columns = ["acc", "train cvg", "null_perc"]

    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    # save result
    output_filename = "result.csv"
    res_df.to_csv(
        os.path.join(
            output_dir,
            output_filename
        )
    )
