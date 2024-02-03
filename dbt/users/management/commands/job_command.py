import json
import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
import paramiko
import re
from dbt.analytics.models import (
    Args,
    DBTLogs,
    DBTJobs,
    GitRepo,
    SubProcessLog,
    ProfileYAML,
    PeriodicTask,
)
from dbt.utils.common import save_profile_yml

SSH_KEY_PREFIX = "git-django_"


class Command(BaseCommand):
    help = "DBT jobs"

    def add_arguments(self, parser):
        print("add_arguments", parser)
        parser.add_argument("--dbt_command", action="store", type=str)
        parser.add_argument(
            "--pk", action="store", type=str
        )  # pk is git repo object id

    def read_json(self, filename, pk):
        DBT_LOG_TARGET = "{}-{}/target".format(
            getattr(settings, "EXTERNAL_REPO_PREFIX"), pk
        )
        file_path = os.path.join(DBT_LOG_TARGET, filename)
        data = {}
        try:
            with open(file_path, "r") as state:
                data = json.load(state)
        except Exception:
            print(f"{file_path} not found")
            data = {}
        return data

    def handle(self, *args, **options):
        os.environ["PATH"] += os.pathsep + "/usr/bin"
        os.environ["PATH"] += os.pathsep + "/bin"

        stdout_data = ""
        dbt_log=None

        try:
            print("*****************welcome to try of handle*********************")
            # dbt_command = options["dbt_command"]
            dbt_command = eval(options["dbt_command"])
            pk = json.loads(options["pk"].replace("'", '"'))["task_id"]
            print(pk ,"task id")
            print(dbt_command,"**************dbt_command")
            
            # if dbt_command.startswith("dbt"):
            # if dbt_command[0].startswith(("dbt","you_can_add_anything_here_but_not_recommended")) :
            
            instance = PeriodicTask.objects.get(id=pk)
            git_repo = GitRepo.objects.get(id=instance.git_repo_id)
            profile_yml = ProfileYAML.objects.get(id=instance.profile_yml_id)
            dbt_command[0].startswith(("dbt","python","you_can_add_anything_here_but_not_recommended")) == True

            EXTERNAL_REPO_PREFIX = getattr(settings, "EXTERNAL_REPO_PREFIX")
            THIS_PROJECT_PATH = getattr(settings, "THIS_PROJECT_PATH")
            EXTERNAL_REPO_NAME = f"{EXTERNAL_REPO_PREFIX}-{instance.git_repo_id}"
            EXTERNAL_REPO_PATH = os.path.join(THIS_PROJECT_PATH, EXTERNAL_REPO_NAME)

            os.path.join(THIS_PROJECT_PATH, EXTERNAL_REPO_NAME)
            pull_cmd = f"cd {EXTERNAL_REPO_PATH} && git pull origin HEAD"
            print(f"Pull cmd: {pull_cmd}")

            profile_yml_content = None
            if instance.profile_yml:
                profile_yml_content = profile_yml.profile_yml
                save_profile_yml(profile_yml_content, ".dbt/profiles.yml")
            else:
                print("No profile yml found")
                exit(-1)

            try :
                print("*******************try*************************")
                # jobid=DBTJobs.objects.all()[len(DBTJobs.objects.all())-1].job_id()
                jobid=DBTJobs.objects.last().job_id
                jobid+=1
                print(jobid)
                print("******************try**************************")
            except:
                print("******************except**************************")
                jobid=1
                print(jobid)
                print("******************except**************************")

                
            dbt_job = DBTJobs.objects.create(
                job_id=jobid,
                task_id=pk,
                created_at=datetime.now(),
                commands=dbt_command,
                completed_at=datetime.now(),
                repository = instance.git_repo.name,
                profile_yml = profile_yml.name,
                periodic_task = instance.name,
                status="initiated"
            )

            if dbt_command[0].startswith(("dbt","python","you_can_add_anything_here_but_not_recommended")) :
                
                print('python or dbt ********************************************************') 

                if git_repo.url.startswith("git"):
                    pvt_key = os.path.join(
                        os.getenv("HOME"),
                        ".ssh/{}{}".format(SSH_KEY_PREFIX, git_repo.ssh_key.id),
                    )
                    cmd = 'eval "$(/usr/bin/ssh-agent -s)" && /usr/bin/ssh-add {} && {}'.format(
                        pvt_key, pull_cmd
                    )
                    p1 = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                    )
                else:
                    p1 = subprocess.Popen(
                        pull_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True,
                    )
                p1.wait()
                SubProcessLog.objects.create(details=str(p1))
                p1.kill()
                del p1
                


                for index,i in enumerate(dbt_command):     

                    dbt_log = DBTLogs.objects.create(
                        job_id=jobid,
                        manifest={},
                        run_results={},
                        sources={},
                        catalog={},
                        command=i,
                        success=False,
                        repository_used_name=instance.git_repo.name,
                        profile_yml_used_name=profile_yml.name,
                        status="initiated",
                        periodic_task_name=instance.name,
                        created_at=datetime.now(),
                        completed_at=datetime.now(),
                        previous_command="this is first commands"
                        if not DBTLogs.objects.all().exists()
                        else DBTLogs.objects.last().command,
                        dbt_stdout="",
                    )

                    run_results = {}

                    args = run_results.get("args", {})
                    dbt_args=Args.objects.create(
                        dbt_log=dbt_log,
                        quiet=args.get("quiet", ""),
                        which=args.get("which", ""),
                        no_print=args.get("no_print", ""),
                        rpc_method=args.get("rpc_method", ""),
                        use_colors=args.get("use_colors", ""),
                        write_json=args.get(" write_json", ""),
                        profiles_dir=args.get("profiles_dir", ""),
                        partial_parse=args.get("partial_parse", ""),
                        printer_width=args.get("printer_width", ""),
                        static_parser=args.get("static_parser", ""),
                        version_check=args.get("version_check", ""),
                        event_buffer_size=args.get("event_buffer_size", ""),
                        indirect_selection=args.get("indirect_selection", ""),
                        send_anonymous=args.get("send_anonymous_usage_stats", ""),
                        usage_stats=args.get("usage_stats", ""),
                    )

                    creation_time=datetime.now()
             
                    
                    executable_command = "cd {} && {}".format(
                        EXTERNAL_REPO_PATH, i
                        #   dbt_command,     # instead of i in original code
                    )
                    
                    dbt_result = subprocess.Popen(
                        executable_command,
                        cwd=EXTERNAL_REPO_PATH,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                    # Read the real-time output from stdout and save it to a variable
                    stdout_data=""
                    for line in dbt_result.stdout:
                        print(line, end="")
                        # stdout_data += re.compile(r'\x1b\[[0-9;]*[mK]').sub('', line.decode("utf-8"))
                        stdout_data += line.decode("utf-8")
                        dbt_log.dbt_stdout=stdout_data
                        dbt_log.save()
                    
                    dbt_result.wait()

                    # Define multiple patterns, including a regular expression and a normal string
                    error_patterns = [
                        re.compile(r"ERROR=(\d+)"),
                        "Encountered an error:",
                        # Add more patterns as needed
                    ]

                    # Function to check if any of the patterns indicate an error
                    def check_for_error(data):
                        for pattern in error_patterns:
                            if isinstance(pattern, str):
                                if pattern in data:
                                    return True
                            elif isinstance(pattern, re.Pattern):
                            # else:
                                match = pattern.search(data)
                                if match and int(match.group(1)) != 0:
                                    return True
                        return False

                    # Check for errors and raise an exception if any
                    if check_for_error(stdout_data):
                        raise Exception(f" ERROR in dbt: \n {stdout_data}")

                    
                    print(f"**************command stdout {i} start")
                    print(stdout_data)
                    print(f"**************command stdout {i} end")

                    print("reading_jsons_start********************************************")
                    os.system("cd {} && git pull origin HEAD".format(EXTERNAL_REPO_PATH))

                    manifest = self.read_json(
                        f"{EXTERNAL_REPO_PATH}/target/manifest.json", instance.git_repo_id
                    )
                    run_results = self.read_json(
                        f"{EXTERNAL_REPO_PATH}/target/run_results.json",
                        instance.git_repo_id,
                    )
                    sources = self.read_json(
                        f"{EXTERNAL_REPO_PATH}/target/sources.json", instance.git_repo_id
                    )
                    catalog = self.read_json(
                        f"{EXTERNAL_REPO_PATH}/target/catalog.json", instance.git_repo_id
                    )
                    print("reading_jsons_end********************************************")
                        # dbt_log.manifest= str(manifest)
                        # dbt_log.run_results=str(run_results)
                        # dbt_log.sources=str(sources)
                        # dbt_log.catalog=str(catalog)
                    dbt_log.manifest= manifest
                    dbt_log.run_results=run_results
                    dbt_log.sources=sources
                    dbt_log.catalog=catalog
                    dbt_log.periodic_task_name=instance.name
                    dbt_log.status="completed"
                    dbt_log.created_at=creation_time
                    dbt_log.completed_at=datetime.now()
                    dbt_log.dbt_stdout=stdout_data
                    dbt_log.success=True

                    dbt_log.save()

                    del stdout_data

                    args = run_results.get("args", {})
                    dbt_args.dbt_log=dbt_log
                    dbt_args.quiet=args.get("quiet", "")
                    dbt_args.which=args.get("which", "")
                    dbt_args.no_print=args.get("no_print", "")
                    dbt_args.rpc_method=args.get("rpc_method", "")
                    dbt_args.use_colors=args.get("use_colors", "")
                    dbt_args.write_json=args.get(" write_json", "")
                    dbt_args.profiles_dir=args.get("profiles_dir", "")
                    dbt_args.partial_parse=args.get("partial_parse", "")
                    dbt_args.printer_width=args.get("printer_width", "")
                    dbt_args.static_parser=args.get("static_parser", "")
                    dbt_args.version_check=args.get("version_check", "")
                    dbt_args.event_buffer_size=args.get("event_buffer_size", "")
                    dbt_args.indirect_selection=args.get("indirect_selection", "")
                    dbt_args.send_anonymous=args.get("send_anonymous_usage_stats", "")
                    dbt_args.usage_stats=args.get("usage_stats", "")

                    dbt_args.save()

                    dbt_result.kill()
                    del dbt_result

                print("***********job_completion**********")
                dbt_job.completed_at=datetime.now()
                dbt_job.periodic_task=instance.name
                dbt_job.status="completed"
                dbt_job.save()
                print(dbt_job.completed_at)
                print("**************")
                print(datetime.now())
                print("***********job_completion**********")   
            else:
                print('not dbt ********************************************************')
                raise Exception("Not DBT Command, only dbt commands allowed")
            
        except Exception as err:
            print("***************************Exception****************")
            print(err,"error from raised exception")
            try:
                print("***************************Exception sub try****************")
                dbt_result.kill()
                del dbt_result
                raise Exception(err)
            except Exception as err_inner:
                print("***************************Exception sub except****************")
                print("***************************Exception sub except and err below****************")
                print(err_inner)
                print("***************************Exception sub except and err above****************")
                pass

            instance = PeriodicTask.objects.get(id=pk)
            
            if dbt_log:
            # if 'dbt_log' in locals() or 'dbt_log' in globals() and dbt_log is not None:
                print("***************************Exception sub if****************")
                print(dbt_log.command)
                print("************")
                dbt_log.command=dbt_log.command
                dbt_log.repository_used_name=instance.git_repo.name
                dbt_log.profile_yml_used_name=profile_yml.name
                dbt_log.periodic_task_name=instance.name
                dbt_log.created_at=creation_time
                dbt_log.completed_at=datetime.now()
                dbt_log.previous_command="this is first commands"
                dbt_log.success=False
                dbt_log.fail_reason=str(err)
                dbt_log.dbt_stdout=str(err)
                dbt_log.status="ERROR"
                dbt_log.save()  

                dbt_job.job_id=jobid
                dbt_job.repository=instance.git_repo.name
                dbt_job.profile_yml=profile_yml.name
                dbt_job.periodic_task=instance.name
                dbt_job.created_at=creation_time
                dbt_job.completed_at=datetime.now()
                dbt_job.success=False
                dbt_job.fail_reason=str(err)
                dbt_job.status="ERROR"
                dbt_job.save()

            else:
                print("***************************Exception sub else****************")

                DBTLogs.objects.create(
                    command=dbt_command,
                    periodic_task_name=instance.name,
                    completed_at=datetime.now(),
                    repository_used_name=instance.git_repo.name,
                    profile_yml_used_name=profile_yml.name,
                    previous_command="this is first commands"
                    if not DBTLogs.objects.all().exists()
                    else DBTLogs.objects.last().command,
                    success=False,
                    fail_reason=str(err),
                    dbt_stdout=stdout_data,
                    status="ERROR"
                )

                DBTJobs.objects.create(
                    job_id=jobid,
                    created_at=datetime.now(),
                    commands=str(dbt_command),
                    completed_at=datetime.now(),
                    repository = instance.git_repo.name,
                    profile_yml = profile_yml.name,
                    periodic_task = instance.name,
                    status="ERROR",
                    success=False,
                    fail_reason=str(err)
                )