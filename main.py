from __future__ import division, print_function, absolute_import
import os
import time
import logging
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, GoogleCloudOptions, StandardOptions
from apache_beam.dataframe.io import read_csv
from apache_beam.dataframe.convert import to_pcollection
#from transformations.db import ReadFromDBFn

logging.getLogger().setLevel(logging.INFO)
logging.info("Building pipeline ...")


class RowReader(beam.DoFn):
    def process(self, row):
        yield {
            'address_id': str(row[0]),
            'available_technology_type': str(row[1]),
            'current_technology_type': str(row[2]),
            'product_availability': str(row[3]),
            'hsicDownspeed': row[4] and int(row[4]),
            'existing_product':str(row[5]),
            'contract_status': str(row[6]),
            'ltCurrentValue': str(row[7]),
            'ltPotentialValue': str(row[8]),
            'drop_status': str(row[9]),
            'copper_port_availability': str(row[10]),
            'demographics': str(row[11]),
            'first_nations': eval(str(row[12])),
            'action': str(row[13]),
            'modified_at': str(row[14]),
            'modified_by': 'APP_HSM_ETL'
        } 

def run():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Load from CSV into CloudSQL')
    parser.add_argument('--project',required=True, help='Specify Google Cloud project')
    parser.add_argument('--region', required=True, help='Specify Google Cloud region')
    parser.add_argument('--input_path', required=True, help='Specify Cloud Storage file path')
    parser.add_argument('--staging_location', required=True, help='Specify Cloud Storage bucket for staging')
    parser.add_argument('--temp_location', required=True, help='Specify Cloud Storage bucket for temp')
    parser.add_argument('--runner', required=True, help='Specify Apache Beam Runner')
    parser.add_argument('--service_account_email', required=True, help='Run job with service account credentials')
    parser.add_argument('--network', required=True, help='Specify Google Network to run workers')
    parser.add_argument('--subnetwork', required=True, help='Specify Google subnetwork to run workers')
    parser.add_argument('--db-url', required=False, dest='db_url')
    parser.add_argument('--template_location', required=False, dest='Specify Google Storage bucket in which to save template')
    parser.add_argument('--setup_file', required=False, dest='Specify setup')
    parser.add_argument('--sdk_container_image', required=False, dest='Specify setup')
    parser.add_argument('--experiment', required=False, dest='Specify setup')

    opts = parser.parse_args()

    # Setting up the Beam pipeline options
    options = PipelineOptions()
    options.view_as(GoogleCloudOptions).project = opts.project
    options.view_as(GoogleCloudOptions).region = opts.region
    options.view_as(GoogleCloudOptions).staging_location = opts.staging_location
    options.view_as(GoogleCloudOptions).temp_location = opts.temp_location
    options.view_as(GoogleCloudOptions).service_account_email = opts.service_account_email
    options.view_as(GoogleCloudOptions).job_name = '{0}{1}'.format('hsm-pipeline-',time.time_ns())
    options.view_as(StandardOptions).runner = opts.runner

    # Static input and output
    #input = 'gs://{0}/MariaTestCSV.csv'.format(opts.project)
    input_path = opts.input_path

    # Create the pipeline
    options.view_as(SetupOptions).save_main_session = True
    with beam.Pipeline(options=options) as p:
        df = (
            p
            | read_csv(input_path, header=0)
        )
        pc = to_pcollection(df)
        _ = (
                pc
                | 'Decode from CSV' >> beam.ParDo(RowReader())
                | 'Print'       >> beam.Map(print)
            )


if __name__ == '__main__':
    run()
