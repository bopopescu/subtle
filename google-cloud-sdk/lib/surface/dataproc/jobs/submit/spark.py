# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Submit a Spark job to a cluster."""

import argparse

from apitools.base.py import encoding

from googlecloudsdk.api_lib.dataproc import base_classes
from googlecloudsdk.api_lib.dataproc import exceptions
from googlecloudsdk.api_lib.dataproc import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.GA)
class Spark(base_classes.JobSubmitter):
  """Submit a Spark job to a cluster.

  Submit a Spark job to a cluster.

  ## EXAMPLES

  To submit a Spark job that runs the main class of a jar, run:

    $ {command} --cluster my_cluster --jar my_jar.jar arg1 arg2

  To submit a Spark job that runs a specific class of a jar, run:

    $ {command} --cluster my_cluster --class org.my.main.Class --jars my_jar1.jar,my_jar2.jar arg1 arg2

  To submit a Spark job that runs a jar that is already on the cluster, run:

    $ {command} --cluster my_cluster --class org.apache.spark.examples.SparkPi --jars file:///usr/lib/spark/lib/spark-examples.jar 1000
  """

  @staticmethod
  def Args(parser):
    super(Spark, Spark).Args(parser)
    SparkBase.Args(parser)
    driver_group = parser.add_argument_group()
    util.AddJvmDriverFlags(driver_group)

  def ConfigureJob(self, job, args):
    SparkBase.ConfigureJob(
        self.context['dataproc_messages'],
        job,
        self.BuildLoggingConfig(args.driver_log_levels),
        self.files_by_type,
        args)
    super(Spark, self).ConfigureJob(job, args)

  def PopulateFilesByType(self, args):
    self.files_by_type.update(SparkBase.GetFilesByType(args))


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class SparkBeta(base_classes.JobSubmitterBeta):
  """Submit a Spark job to a cluster.

  Submit a Spark job to a cluster.

  ## EXAMPLES

  To submit a Spark job that runs the main class of a jar, run:

    $ {command} --cluster my_cluster --jar my_jar.jar arg1 arg2

  To submit a Spark job that runs a specific class of a jar, run:

    $ {command} --cluster my_cluster --class org.my.main.Class --jars my_jar1.jar,my_jar2.jar arg1 arg2

  To submit a Spark job that runs a jar that is already on the cluster, run:

    $ {command} --cluster my_cluster --class org.apache.spark.examples.SparkPi --jars file:///usr/lib/spark/lib/spark-examples.jar 1000
  """

  @staticmethod
  def Args(parser):
    super(SparkBeta, SparkBeta).Args(parser)
    SparkBase.Args(parser)
    driver_group = parser.add_mutually_exclusive_group(required=True)
    util.AddJvmDriverFlags(driver_group)

  def ConfigureJob(self, job, args):
    SparkBase.ConfigureJob(
        self.context['dataproc_messages'],
        job,
        self.BuildLoggingConfig(args.driver_log_levels),
        self.files_by_type,
        args)
    super(SparkBeta, self).ConfigureJob(job, args)

  def PopulateFilesByType(self, args):
    self.files_by_type.update(SparkBase.GetFilesByType(args))


class SparkBase(object):
  """Submit a Java or Scala Spark job to a cluster."""

  @staticmethod
  def Args(parser):
    """Parses command-line arguments specific to submitting Spark jobs."""
    parser.add_argument(
        '--jars',
        type=arg_parsers.ArgList(),
        metavar='JAR',
        default=[],
        help=('Comma separated list of jar files to be provided to the '
              'executor and driver classpaths.'))
    parser.add_argument(
        '--files',
        type=arg_parsers.ArgList(),
        metavar='FILE',
        default=[],
        help='Comma separated list of files to be provided to the job.')
    parser.add_argument(
        '--archives',
        type=arg_parsers.ArgList(),
        metavar='ARCHIVE',
        default=[],
        help=('Comma separated list of archives to be provided to the job. '
              'must be one of the following file formats: .zip, .tar, .tar.gz, '
              'or .tgz.'))
    parser.add_argument(
        'job_args',
        nargs=argparse.REMAINDER,
        help='The arguments to pass to the driver.')
    parser.add_argument(
        '--properties',
        type=arg_parsers.ArgDict(),
        metavar='PROPERTY=VALUE',
        help='A list of key value pairs to configure Spark.')
    parser.add_argument(
        '--driver-log-levels',
        type=arg_parsers.ArgDict(),
        metavar='PACKAGE=LEVEL',
        help=('A list of package to log4j log level pairs to configure driver '
              'logging. For example: root=FATAL,com.example=INFO'))

  @staticmethod
  def GetFilesByType(args):
    """Returns a dict of files by their type (jars, archives, etc.)."""
    # TODO(user): Move arg manipulation elsewhere.
    # TODO(user): Remove with GA flags 2017-04-01 (b/33298024).
    if not args.main_class and not args.main_jar:
      raise exceptions.ArgumentError('Must either specify --class or JAR.')
    if args.main_class and args.main_jar:
      log.warn(
          'You must specify exactly one of --jar and --class. '
          'This will be strictly enforced in April 2017. '
          "Use 'gcloud beta dataproc jobs submit spark' to see new behavior.")
      log.info('Passing main jar as an additional jar.')
      args.jars.append(args.main_jar)
      args.main_jar = None

    return {
        'main_jar': args.main_jar,
        'jars': args.jars,
        'archives': args.archives,
        'files': args.files}

  @staticmethod
  def ConfigureJob(messages, job, log_config, files_by_type, args):
    """Populates the sparkJob member of the given job."""

    spark_job = messages.SparkJob(
        args=args.job_args,
        archiveUris=files_by_type['archives'],
        fileUris=files_by_type['files'],
        jarFileUris=files_by_type['jars'],
        mainClass=args.main_class,
        mainJarFileUri=files_by_type['main_jar'],
        loggingConfig=log_config)

    if args.properties:
      spark_job.properties = encoding.DictToMessage(
          args.properties, messages.SparkJob.PropertiesValue)

    job.sparkJob = spark_job
