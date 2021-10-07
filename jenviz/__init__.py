#!/usr/bin/python3

import argparse
import configparser
import os
import sys

import jenkins

from graphviz import Digraph


FONTSIZE_SMALL = 11


def _job_build_parameters_as_html(jenkins, job):
    build_info = jenkins.get_build_info(job['name'], job['lastBuild']['number'])
    html = ''
    for action in build_info['actions']:
        if not action.get('_class', None) == 'hudson.model.ParametersAction':
            continue
        html = f"""
<TR><TD HREF="{build_info["url"]}"><FONT POINT-SIZE="{FONTSIZE_SMALL}">
<B>Parameters (build #{job["lastBuild"]["number"]}, {build_info["result"]})</B></FONT></TD></TR>
"""
        for param in action['parameters']:
            html += f'<TR><TD><FONT POINT-SIZE="{FONTSIZE_SMALL}">{param["name"]}: {param["value"]}</FONT></TD></TR>'
    return html


def _job_parameters_as_html(job):
    """
    jobs that do not have a build yet
    """
    html = ''
    for action in job['actions']:
        if not action.get('_class', None) == 'hudson.model.ParametersDefinitionProperty':
            continue
        html = f'<TR><TD><FONT POINT-SIZE="{FONTSIZE_SMALL}"><B>Parameters (no build yet)</B></FONT></TD></TR>'
        for param in action['parameterDefinitions']:
            html += f'<TR><TD><FONT POINT-SIZE="{FONTSIZE_SMALL}">{param["name"]}</FONT></TD></TR>'
    return html


def _job_as_html(jenkins, job):

    bgcolor = 'BGCOLOR="grey"' if hasattr(job, 'disabled') and job['disabled'] else ''
    html = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" {bgcolor}>'
    html += f'<TR><TD HREF="{job["url"]}">{job["name"]}'
    html += f'{" (disabled)" if hasattr(job, "disabled") and job["disabled"] else ""}</TD></TR>'
    html += f'<TR><TD><FONT POINT-SIZE="{FONTSIZE_SMALL}">{job["_class"]}</FONT></TD></TR>'
    if job.get('lastBuild', None):
        html += _job_build_parameters_as_html(jenkins, job)
    else:
        html += _job_parameters_as_html(job)
    html += '</TABLE>>'
    return html


def _graph_create(graph, jenkins, job_name, job_ignore, job_ignore_disabled, job_ignore_nobuild):
    """
    Recursive job downstream graph creation
    """
    job = jenkins.get_job_info(job_name)
    job_label = _job_as_html(jenkins, job)
    graph.node(job['name'], label=job_label, shape='plaintext')
    for downstream_job in job['downstreamProjects']:
        downstream_job = jenkins.get_job_info(downstream_job['name'])
        if downstream_job['name'] in job_ignore:
            print(f'job "{downstream_job["name"]}" in ignore list. skipping ...')
            continue
        if job_ignore_disabled:
            if hasattr(downstream_job, 'disabled') and downstream_job['disabled'] is True:
                print(f'job "{downstream_job["name"]}" disabled. skipping ...')
                continue
        if job_ignore_nobuild:
            if downstream_job['color'] == 'notbuilt':
                continue
        _graph_create(graph, jenkins, downstream_job['name'], job_ignore, job_ignore_disabled, job_ignore_nobuild)
        graph.edge(job['name'], downstream_job['name'])


def _jenkins(url, user, password):
    """get a jenkinsapi jenkins instance"""
    j = jenkins.Jenkins(url,
                        username=user,
                        password=password)
    return j


def _get_profile(args):
    if not os.path.exists(args.jenviz_config_file):
        print(f'jenviz configuration file {args.jenviz_config_file} does not exist')
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(args.jenviz_config_file)
    if args.jenviz_config_profile not in config:
        print(f'can not find section {args.jenviz_config_profile} in {args.jenviz_config_file}')
        sys.exit(1)
    if 'url' not in config[args.jenviz_config_profile]:
        print(f'url not in profile {args.jenviz_config_profile}')
        sys.exit(1)
    if 'user' not in config[args.jenviz_config_profile]:
        print(f'user not in profile {args.jenviz_config_profile}')
        sys.exit(1)
    if 'password' not in config[args.jenviz_config_profile]:
        print(f'password not in profile {args.jenviz_config_profile}')
        sys.exit(1)
    return (config[args.jenviz_config_profile]['url'],
            config[args.jenviz_config_profile]['user'],
            config[args.jenviz_config_profile]['password'])


def _parser():
    parser = argparse.ArgumentParser(
        description='Visualize Jenkins jobs')
    jenkins_group = parser.add_argument_group(title='Jenkins')
    jenkins_group.add_argument('--jenviz-config-file', '-c',
                               default=os.path.join(os.path.expanduser('~'), '.config', 'jenviz.ini'),
                               help='Path to the jenviz configuration file. Default: %(default)s')
    jenkins_group.add_argument('--jenviz-config-profile', '-p',
                               help='The profile (section) to use in the jenviz-config-file')
    jenkins_group.add_argument('--jenkins-url', help='The Jenkins url')
    jenkins_group.add_argument('--jenkins-user', help='The Jenkins username')
    jenkins_group.add_argument('--jenkins-password', help='The Jenkins password')
    parser.add_argument('--job-ignore', help='Jenkins job name to ignore', action='append', default=[])
    parser.add_argument('--job-ignore-disabled', help='Ignore disabled Jenkins jobs', action='store_true')
    parser.add_argument('--job-ignore-nobuild', help='Ignore Jenkins jobs that have no last build',
                        action='store_true')
    parser.add_argument('--output-file', help='The rendered output filename', default='jenviz.out')
    parser.add_argument('--output-format', help='The format to render the file to. Default: %(default)s',
                        default='pdf')
    parser.add_argument('--output-view', help='View the output when done. Default: %(default)s',
                        action='store_true')
    parser.add_argument('job_name', metavar='job-name', help='the Jenkins job name')
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()
    if args.jenviz_config_profile:
        url, user, password = _get_profile(args)
    else:
        url = args.jenkins_url
        user = args.jenkins_user
        password = args.jenkins_password
    jenkins = _jenkins(url, user, password)
    graph = Digraph(comment='Jenkins jobs', name=args.job_name)
    _graph_create(graph, jenkins, args.job_name, args.job_ignore, args.job_ignore_disabled,
                  args.job_ignore_nobuild)
    graph.render(args.output_file, format=args.output_format, view=args.output_view)
    print(f"graph written to {args.output_file}.{args.output_format}")


if __name__ == '__main__':
    main()
