import json, os, boto3, sys, time, re, csv


def lambda_handler(event, context):
    account = ''
    report_bucket = ''
    report_date = time.strftime("%Y%m%d", time.localtime(time.time()))
    report_key = 'reports/Report-TagCompliance-' + report_date + '.csv'

    results = []
    all_instance_tags = get_all_instance_tags()
    results.append(all_instance_tags[0])
    print("NonCompliant: " + str(all_instance_tags[1]))
    output_file = create_csv(results)

    s3 = boto3.client('s3')
    s3.put_object(Bucket=report_bucket, Key=report_key, Body=str(output_file))


def get_all_instance_tags():
    required_tags = json.loads(required_tags_config)['RequiredTags']
    rows = []
    count = 0
    ec2 = boto3.client('ec2')
    for reservations in ec2.describe_instances()['Reservations']:

        for instance in reservations['Instances']:
            instance_header = []
            instance_header.append(instance['InstanceId'])
            instance_header.append('---')
            instance_header.append('---')
            rows.append(instance_header)
            compliance_check = []
            instance_tags = instance.get('Tags')
            if instance_tags:
                tag_status = verify_tags(required_tags, instance_tags)

                for compliance, tags in tag_status.items():
                    if not tags == None:
                        for tag in tags:
                            tag_row = []
                            tag_row.append('')
                            tag_row.append(str(tag['Key']))
                            tag_row.append(str(tag['Value']))
                            tag_row.append(str(compliance))
                            rows.append(tag_row)
                            compliance_check.append(str(compliance))
            else:
                tag_row = []
                tag_row.append('')
                tag_row.append('ALL')
                tag_row.append('')
                tag_row.append('NON-COMPLIANT')
                rows.append(tag_row)
                compliance_check.append(str(compliance))

            if 'NON-COMPLIANT' in compliance_check:
                count += 1
            rows.append('')

    return rows, count


def create_csv(output):
    header_row = ['InstanceId', 'TagKey', 'TagValue', 'Compliance']
    csv = ",".join(header_row)
    for rows in output[0]:
        new_row = ",".join(rows)
        csv = "\n".join([csv, new_row])

    return csv


def verify_tags(required_tags, instance_tags):
    tag_status = {}
    tag_status['COMPLIANT'] = []
    tag_status['NON-COMPLIANT'] = []

    tag_k = []
    tag_v = []

    for tag in instance_tags:
        tag_k.append(str(tag['Key']).strip())
        tag_v.append(str(tag['Value']).strip())

    instance_tag_dict = dict(zip(tag_k, tag_v))

    for tag, options in required_tags.items():

        current_value = False
        in_scope = False
        required = options['required']

        if tag in instance_tag_dict:
            in_scope = True
            current_value = instance_tag_dict[tag]

        elif tag == 'ECS:Scheduler:ec2-startstop' and any(
                instance_tag_key.startswith(tag) for instance_tag_key in instance_tag_dict):
            in_scope = True
            current_value = [instance_tag_dict[key] for key in instance_tag_dict.keys() if key.startswith(tag)][0]

        else:
            if required:
                in_scope = False
                current_value = False
                tag_status['NON-COMPLIANT'].append({'Key': str(tag), 'Value': ''})
            else:
                pass

        if in_scope:
            if verify_tag_value(current_value, options['values'], required=required):
                tag_status['COMPLIANT'].append({'Key': tag, 'Value': current_value})
            else:
                tag_status['NON-COMPLIANT'].append({'Key': tag, 'Value': current_value})

    return tag_status


def verify_tag_value(current, possible, required=True):
    if possible and current:
        for string in possible:
            regex = re.compile(string)
            if regex.match(current) is not None:
                break
        else:
            return False
    elif required and not current:
        return False

    return True


required_tags_config = '''
{
 "RequiredTags": {
      "Name": {
        "required": true,
        "values": []
      },
      "ECS:ServerFunction": {
        "required": true,
        "values": []
      },
      "ECS:System": {
        "required": true,
        "values": [
          "ActiveDirectory",
          "Apigee",
          "Benefits/C3Lan",
          "Benefits/C3Mf",
          "Benefits/Claims4",
          "Benefits/Cpstr",
          "Benefits/Epms",
          "Benefits/Icms",
          "Benefits/Nps",
          "Benefits/Raps",
          "Benefits/Smi",
          "Biometrics/Cpms",
          "Biometrics/Fd258",
          "Biometrics/Nass",
          "CustomerService/Cmis",
          "CustomerService/Cris",
          "CustomerService/Cswp",
          "CustomerService/EccCecIva",
          "Dbis/EciscorBigData",
          "Dbis/EciscorInformatica",
          "Dbis/EciscorOracle",
          "Dbis/EciscorSas",
          "Dbis/EciscorSasSmart",
          "Dbis/EciscorSmart",
          "Dbis/EciscorSoftNas",
          "Dbis/Stars",
          "DidIt/Other",
          "DIDIT_FS/ColdFusion",
          "DidItFs/Ar11Dis",
          "DidItFs/Bcps",
          "DidItFs/Camino",
          "DidItFs/Cats",
          "DidItFs/Champs",
          "DidItFs/Echo",
          "DidItFs/Efrs",
          "DidItFs/EPulse",
          "DidItFs/Faccon",
          "DidItFs/Fish",
          "DidItFs/G22",
          "DidItFs/IClaims",
          "DidItFs/Idcms",
          "DidItFs/Mits",
          "DidItFs/Npwr",
          "DidItFs/OrgChart",
          "DidItFs/PpAlert",
          "DidItFs/Queue",
          "DidItFs/Ross",
          "DidItFs/Scheduler",
          "DidItFs/Sera",
          "DidItRor/AssetManager",
          "DidItRor/AstErrorTracking",
          "DidItRor/Bads",
          "DidItRor/CapTrackerr",
          "DidItRor/Cicd",
          "DidItRor/Dolores",
          "DidItRor/DriveTimeTracker",
          "DidItRor/Eb5Db",
          "DidItRor/EStat",
          "DidItRor/EWrts",
          "DidItRor/Fams",
          "DidItRor/FodCsDb",
          "DidItRor/Fsnw",
          "DidItRor/Icts",
          "DidItRor/Impact",
          "DidItRor/Infact",
          "DidItRor/Ipo",
          "DidItRor/Kedl",
          "DidItRor/Lats",
          "DidItRor/Msi",
          "DidItRor/OitrhDashboard",
          "DidItRor/OpqReportingTools",
          "DidItRor/PassportTracker",
          "DidItRor/Pdcp",
          "DidItRor/QaDb",
          "DidItRor/Rad",
          "DidItRor/Ramt",
          "DidItRor/RideTheTide",
          "DidItRor/UscisAppStore",
          "Elis/Elis2",
          "Esb/EsbAtlas",
          "Esb/EsbCin",
          "Esb/EsbCpmsSS",
          "Esb/EsbCS",
          "Esb/EsbEss",
          "Esb/EsbLis",
          "Esb/EsbPcqs",
          "Esb/EsbPortfolio",
          "Esb/EsbRass",
          "Esb/EsbTss",
          "Esb/EsbVibe",
          "Esb/EsbVSAhs",
          "Esb/EsbVss",
          "Gss/AgileCraft",
          "Gss/Ansible",
          "Gss/Chef",
          "Gss/Ice",
          "Gss/Jenkins",
          "Gss/Jumpbox",
          "Gss/Management",
          "Gss/Networking",
          "Gss/Nexus",
          "Gss/Newrelic",
          "Gss/Puppet",
          "Gss/QualityCenter",
          "Gss/Spacewalk",
          "Gss/Test",
          "Isd/Admin",
          "Isd/EPO",
          "Isd/Fortify",
          "Isd/Hashcat",
          "Isd/Invincea",
          "Isd/Other",
          "Isd/PenTest",
          "Isd/Splunk",
          "Isd/Tenable",
          "Isd/Venafi",
          "Isd/WebInspect",
          "Nioc/CiscoCloudCenter",
          "OpenShift",
          "Osi/CCure",
          "Other/WebInspectEnterprise",
          "Others/Deque",
          "Others/FdnsDs",
          "Others/Github",
          "Others/IcamEnterprise",
          "Others/IcamIdPass",
          "Others/IcamPublic",
          "Others/Itam",
          "Others/MyUscis",
          "Others/Opts",
          "Others/Snow",
          "Pivotal",
          "Records/Cis",
          "Records/Edms",
          "Records/Fips",
          "Records/Ivcs",
          "Records/Midas",
          "Records/Nfts",
          "Records/Soda",
          "Verifications/AvantCrm",
          "Verifications/CaseManagement",
          "Verifications/Dat",
          "Verifications/EccVcc",
          "Verifications/EveMod",
          "Verifications/MyEVerify",
          "Verifications/SaveMod",
          "Verifications/Sid",
          "Verifications/SvsMod",
          "Verifications/Vis",
          "Verifications/VisMod"
        ]
      },
      "ECS:FismaId": {
        "required": true,
        "values": [
          "CIS-[0-9]{5}-(MAJ|SUB|GSS)-[0-9]{5}"
        ]
      },
      "ECS:Environment": {
        "required": true,
        "values": [
          "Prod",
          "PreProd",
          "NonProd",
          "PerformanceTest",
          "Dev",
          "Fqt",
          "DataMigration",
          "Demo",
          "PenTest"
        ]
      },
      "ECS:Poc": {
        "required": true,
        "values": []
      },
      "ECS:Scheduler:ec2-startstop": {
        "required": true,
        "values": []
      }
    }
}
'''
