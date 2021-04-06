import csv
import time


def append_data_to_row(row_with_data, form_attribute_name):
    entity_id = row_with_data[2]
    try:
        id_row = ecmMap[entity_id + form_attribute_name]
        idToValidate = id_row[2]
        row = []
        row.append('US')
        row.append('IL')
        row.append(entity_id)
        row.append(entity_domain)
        row.append(idToValidate)
        row.append(form_attribute_name)
        row.append(row_with_data[3])
        row.append(exemption_domain)
        row.append(row_with_data[4])
        row.append(row_with_data[5])
        row.append(row_with_data[6])
        row.append(row_with_data[7])
        row.append(row_with_data[8])
        row.append(row_with_data[9])
        row.append(row_with_data[10])
        row.append(row_with_data[11])
        return row
    except Exception as e:
        # id = dummyString
        return None


def generate_final_input_csv():
    rows = []
    with open(input_athena, 'r') as athena_file:
        athena_file_reader = csv.reader(athena_file)

        for athenaRow in athena_file_reader:
            if athenaRow[2] != 'entity_id':
                # entity_id = athenaRow[2]
                for form_attribute_name in eligible_form_attribute_names:
                    row_to_append = append_data_to_row(athenaRow, form_attribute_name)
                    if row_to_append is not None:
                        rows.append(row_to_append)

    with open(output_file, "w") as il_witcher_output:
        writer = csv.writer(il_witcher_output, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)


if __name__ == '__main__':
    input_athena = '/Users/rddiwana/Work/IL ENumberVerify/AthenaExtract.csv'
    ecm_input = '/Users/rddiwana/Work/IL ENumberVerify/ECM_Export.csv'
    output_file = '/Users/rddiwana/Work/IL ENumberVerify/final/IL_WitcherInput_temp.csv'
    ecmMap = {}
    entity_domain = 'CustomerId'
    exemption_domain = 'ECMBlanket'

    header = ['jurisdiction_authority_country_code', 'jurisdiction_authority_state_code', 'entity_id', 'entity_domain',
              'original_number_submitted_by_user', 'formAttributeName', 'exemption_id', 'exemption_domain',
              'exemption_type_display_name', 'certificate_id', 'certificate_expiration_date_month_year', 'created_on_date',
              'certificate_effective_date', 'certificate_expiration_date', 'system_effective_date', 'system_end_date']

    dummyString = 'NO_DATA_FOUND'
    eligible_form_attribute_names = ['IL_AccountID_MTC', 'IL_ExemptionNumber_MTC', 'ILStateRegistrationNumber_MTC']

    with open(ecm_input, 'r') as ecm_file:
        start_time_indexing_ECM = time.time()

        ecm_file_reader = csv.reader(ecm_file)
        for row in ecm_file_reader:
            key = row[0] + row[1]
            ecmMap[key] = row

        print('Finished Indexing within: ' + str(round((time.time() - start_time_indexing_ECM) / 60, 2)) + ' Minutes.')
        generate_final_input_csv()

