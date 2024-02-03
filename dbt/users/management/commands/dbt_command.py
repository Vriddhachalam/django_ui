import json
import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
import paramiko
from dbt.analytics.models import (
    Args,
    DBTLogs,
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
        try:
            # dbt_command = options["dbt_command"]
            dbt_command = eval(options["dbt_command"])
            pk = json.loads(options["pk"].replace("'", '"'))["task_id"]
            
            # if dbt_command.startswith("dbt"):
            if dbt_command[0].startswith("dbt"):
                instance = PeriodicTask.objects.get(id=pk)
                git_repo = GitRepo.objects.get(id=instance.git_repo_id)
                profile_yml = ProfileYAML.objects.get(id=instance.profile_yml_id)

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

                all_manifests={}
                all_run_results={}
                all_sources={}
                all_catalogs={}

                dbt_log = DBTLogs.objects.create(
                    manifest=all_manifests,
                    run_results=all_run_results,
                    sources=all_sources,
                    catalog=all_catalogs,
                    command=dbt_command,
                    repository_used_name=instance.git_repo.name,
                    profile_yml_used_name=profile_yml.name,
                    periodic_task_name="NAME: " +instance.name +"\nSTATUS: --initiated",
                    created_at=datetime.now(),
                    completed_at=datetime.now(),
                    previous_command="this is first commands"
                    if not DBTLogs.objects.all().exists()
                    else DBTLogs.objects.last().command,
                    dbt_stdout=stdout_data,
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

                for index,i in enumerate(dbt_command):                   
                    
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
                    for line in dbt_result.stdout:
                        print(line, end="")
                        stdout_data += line.decode("utf-8")

                    dbt_result.wait()
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
                    all_manifests[i]=str(manifest)
                    all_run_results[i]=str(run_results)
                    all_sources[i]=str(sources)
                    all_catalogs[i]=str(catalog)

                    if index == len(dbt_command)-1:

                        dbt_log.manifest= str(all_manifests)
                        dbt_log.run_results=str(all_run_results)
                        dbt_log.sources=str(all_sources)
                        dbt_log.catalog=str(all_catalogs)
                        dbt_log.periodic_task_name= "NAME: " +instance.name +"\nSTATUS: --completed"
                        dbt_log.created_at=creation_time
                        dbt_log.completed_at=datetime.now()
                        dbt_log.dbt_stdout=stdout_data
                        dbt_log.save()

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

        except Exception as err:
            try:
                dbt_result.kill()
                del dbt_result
            except Exception as err:
                pass

            instance = PeriodicTask.objects.get(id=pk)

            if dbt_log:

                dbt_log.command=dbt_command
                dbt_log.repository_used_name=instance.git_repo.name
                dbt_log.profile_yml_used_name=profile_yml.name
                dbt_log.periodic_task_name= "NAME: " +instance.name +"\nSTATUS: --completed"
                dbt_log.created_at=creation_time
                dbt_log.completed_at=datetime.now()
                dbt_log.previous_command="this is first commands"
                dbt_log.success=False,
                dbt_log.fail_reason=str(err),
                dbt_log.dbt_stdout=stdout_data
                dbt_log.dbt_stdout=stdout_data
                dbt_log.save()

            else:

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
                    dbt_stdout=stdout_data
                )
