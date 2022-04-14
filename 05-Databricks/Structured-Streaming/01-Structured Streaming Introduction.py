# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC ### Introduction to Structured Streaming
# MAGIC Structured Streaming is an efficient way to ingest large quantities of data from a variety of sources.  This course is intended to teach you how how to use Structured Streaming to ingest data from files and publisher-subscribe systems. Starting with the fundamentals of streaming systems, we introduce concepts such as reading streaming data, writing out streaming data to directories, displaying streaming data and Triggers. We discuss the problems associated with trying to aggregate streaming data and then teach how to solve this problem using structures called windows and expiring old data using watermarking. Finally, we examine how to connect Structured Streaming with popular publish-subscribe systems to stream data from Wikipedia.
# MAGIC 
# MAGIC #### Objectives
# MAGIC * Read, write and display streaming data.	
# MAGIC * Apply time windows and watermarking to aggregate streaming data.
# MAGIC * Use a publish-subscribe system to stream wikipedia data in order to visualize meaningful analytics
# MAGIC 
# MAGIC First, run the following cell to import the data and make various utilities available for our experimentation.

# COMMAND ----------

# MAGIC %run "./Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC ### The Problem
# MAGIC A stream of data is coming in from a TCP-IP socket, Kafka, EventHub, Kinesis or other sources, but... the data is coming in faster than it can be consumed.
# MAGIC **How can this problem be solved?**
# MAGIC 
# MAGIC #### The Answer... Implement the Micro-Batch Model
# MAGIC Many APIs solve this problem by employing a Micro-Batch model, wherein a *firehose* of data is collected for a predetermined interval of time (the **Trigger Interval**).<br>
# MAGIC In the following illustration, the **Trigger Interval** is two seconds.
# MAGIC 
# MAGIC <img src="https://files.training.databricks.com/images/streaming-timeline.png" style="height: 120px;"/>
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC #### Processing the Micro-Batch
# MAGIC For each interval, the data from the previous [two-second] interval must be processed... even as the next micro-batch of data is being collected.<br>
# MAGIC In the following illustration, two seconds worth of data is being processed in about one second.
# MAGIC 
# MAGIC <img src="https://files.training.databricks.com/images/streaming-timeline-1-sec.png" style="height: 120px;">
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC **But what happens if the data isn't processed quickly enough while reading from the streaming source?** <br>
# MAGIC - If the source were a TCP/IP stream... then data packets would be dropped; i.e., data would be lost.
# MAGIC - If the source were an IoT device measuring the outside temperature every 15 seconds... then this might be OK.<br>
# MAGIC   ...But, if the incoming data represented continuously shifting stock prices... the business impact could be thousands of lost dollars.
# MAGIC - If the source were a Pub/Sub system like Apache Kafka, Azure EventHub or AWS Kinesis... we would simply fall further behind.<br>
# MAGIC   Eventually, the pubsub system would reach its resource limits inducing other problems; however, we could re-launch the cluster using enough CPU cores to catch-up and remain current.
# MAGIC - **Ultimately, the data for the previous interval must be processed before data from the next interval arrives!**
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC #### From Micro-Batch to Table
# MAGIC Apache Spark treats a stream of **micro-batches** as if they were a series of continuous updates to a database table.
# MAGIC - This enables a query to be executed against this **input table**... just as if it were a static database table.
# MAGIC - The computation on the **input table** can then then pushed to a **results table**.
# MAGIC - And finally, the **results table** can be written to an output **sink**. 
# MAGIC 
# MAGIC <img src="https://files.training.databricks.com/images/eLearning/Delta/stream2rows.png" style="height: 200px"/>
# MAGIC 
# MAGIC ##### Spark Structured Streams consist of two parts:
# MAGIC The **Input source** such as 
# MAGIC * Kafka
# MAGIC * Azure Event Hub
# MAGIC * Files on a distributed system
# MAGIC * TCP-IP sockets
# MAGIC   
# MAGIC And the **Sinks** such as
# MAGIC * Kafka
# MAGIC * Azure Event Hub
# MAGIC * Various file formats
# MAGIC * The system console
# MAGIC * Apache Spark tables (memory sinks)
# MAGIC * The completely custom `foreach()` iterator
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC ##### Update Triggers:
# MAGIC **Triggers** can be defined to control how frequently the **input table** is updated. Each time a trigger fires, Spark checks for new data (new rows for the input table), and updates the result.
# MAGIC *The default value for `DataStreamWriter.trigger(Trigger)` is ProcessingTime(0), and it will run the query as fast as possible.*  This process repeats in perpetuity.## End-to-end Fault Tolerance
# MAGIC 
# MAGIC Structured Streaming ensures end-to-end exactly-once fault-tolerance guarantees through _checkpointing_ and <a href="https://en.wikipedia.org/wiki/Write-ahead_logging" target="_blank">Write Ahead Logs</a>.
# MAGIC 
# MAGIC Structured Streaming sources, sinks, and the underlying execution engine work together to track the progress of stream processing. If a failure occurs, the streaming engine attempts to restart and/or reprocess the data.
# MAGIC 
# MAGIC This approach _only_ works if the streaming source is replayable. To ensure fault-tolerance, Structured Streaming assumes that every streaming source has offsets, akin to:
# MAGIC 
# MAGIC * <a target="_blank" href="https://kafka.apache.org/documentation/#intro_topics">Kafka message offsets</a>
# MAGIC * <a target="_blank" href="http://docs.aws.amazon.com/streams/latest/dev/key-concepts.html#sequence-number">Kinesis sequence numbers</a>
# MAGIC 
# MAGIC At a high level, the underlying streaming mechanism relies on a couple approaches:
# MAGIC 
# MAGIC * First, Structured Streaming uses checkpointing and write-ahead logs to record the offset range of data being processed during each trigger interval.
# MAGIC * Next, the streaming sinks are designed to be _idempotent_—that is, multiple writes of the same data (as identified by the offset) do _not_ result in duplicates being written to the sink.
# MAGIC 
# MAGIC Taken together, replayable data sources and idempotent sinks allow Structured Streaming to ensure **end-to-end, exactly-once semantics** under any failure condition.
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC ##### End-to-End Fault Tolerance:
# MAGIC Structured Streaming ensures end-to-end exactly-once fault-tolerance guarantees through _checkpointing_ and <a href="https://en.wikipedia.org/wiki/Write-ahead_logging" target="_blank">Write Ahead Logs</a>.  Structured Streaming sources, sinks, and the underlying execution engine work together to track the progress of stream processing. If a failure occurs, the streaming engine attempts to restart and/or reprocess the data. This approach _only_ works if the streaming source is replayable. To ensure fault-tolerance, Structured Streaming assumes that every streaming source has offsets, akin to:
# MAGIC * <a target="_blank" href="https://kafka.apache.org/documentation/#intro_topics">Kafka message offsets</a>
# MAGIC * <a target="_blank" href="http://docs.aws.amazon.com/streams/latest/dev/key-concepts.html#sequence-number">Kinesis sequence numbers</a>
# MAGIC 
# MAGIC At a high level, the underlying streaming mechanism relies on a couple approaches:
# MAGIC * First, Structured Streaming uses checkpointing and write-ahead logs to record the offset range of data being processed during each trigger interval.
# MAGIC * Next, the streaming sinks are designed to be _idempotent_—that is, multiple writes of the same data (as identified by the offset) do _not_ result in duplicates being written to the sink.
# MAGIC 
# MAGIC Taken together, replayable data sources and idempotent sinks allow Structured Streaming to ensure **end-to-end, exactly-once semantics** under any failure condition.

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.0 Reading a Stream
# MAGIC The method `SparkSession.readStream` returns a `DataStreamReader` used to configure the stream.
# MAGIC There are a number of key points to the configuration of a `DataStreamReader`:
# MAGIC * The schema
# MAGIC * The type of stream: Files, Kafka, TCP/IP, etc
# MAGIC * Configuration specific to the type of stream
# MAGIC   * For files, the file type, the path to the files, max files, etc...
# MAGIC   * For TCP/IP the server's address, port number, etc...
# MAGIC   * For Kafka the server's address, port, topics, partitions, etc...
# MAGIC   
# MAGIC   
# MAGIC ##### 1.1. Defining the Schema:
# MAGIC Every streaming DataFrame must have a schema - the definition of column names and data types.
# MAGIC - Some sources such as Kafka define the schema for you.
# MAGIC - In file-based streaming sources, for example, the schema is user-defined.

# COMMAND ----------

# Define the schema using a DDL-formatted string.
dataSchema = "Recorded_At timestamp, Device string, Index long, Model string, User string, _corrupt_record String, gt string, x double, y double, z double"

# COMMAND ----------

# MAGIC %md
# MAGIC ##### 1.2. Configuring a File Stream
# MAGIC In our example below, we will be consuming files written continuously to a pre-defined directory. 
# MAGIC To control how much data is pulled into Spark at once, we can specify the option `maxFilesPerTrigger`.
# MAGIC In the example below, only one file is read in for every trigger interval: `dsr.option("maxFilesPerTrigger", 1)` <br>
# MAGIC Both the location and file type are specified with the following call, which itself returns a `DataFrame`: `df = dsr.json(dataPath)`

# COMMAND ----------

dataPath = "dbfs:/mnt/training/definitive-guide/data/activity-data-stream.json"
initialDF = (spark
  .readStream                            # Returns DataStreamReader
  .option("maxFilesPerTrigger", 1)       # Force processing of only 1 file per trigger 
  .schema(dataSchema)                    # Required for all streaming DataFrames
  .json(dataPath)                        # The stream's source directory and file type
)

# COMMAND ----------

# MAGIC %md
# MAGIC Given an initial `DataFrame`, transformations can then be applied. The example below illustrates renaming a column and removing an unnecessary column from the schema:

# COMMAND ----------

streamingDF = (initialDF
  .withColumnRenamed("Index", "User_ID")  # Pick a "better" column name
  .drop("_corrupt_record")                # Remove an unnecessary column
)

# COMMAND ----------

# MAGIC %md
# MAGIC ##### 1.3. Streaming DataFrames
# MAGIC Other than the call to `spark.readStream`, it looks just like any other `DataFrame`... But is it a "streaming" `DataFrame`?
# MAGIC You can differentiate between a "static" and "streaming" `DataFrame` with the following call:

# COMMAND ----------

streamingDF.isStreaming

# COMMAND ----------

# MAGIC %md
# MAGIC ##### 1.4. Unsupported Operations
# MAGIC Most operations on a "streaming" DataFrame are identical to a "static" DataFrame; however, there are some exceptions:
# MAGIC * Sorting a never-ending stream by `Recorded_At`.
# MAGIC * Aggregating a stream by some criterion.
# MAGIC 
# MAGIC Next, we will illustrate how to solve this problem.

# COMMAND ----------

from pyspark.sql.functions import col

try:
  sortedDF = streamingDF.orderBy(col("Recorded_At").desc())
  display(sortedDF)
except:
  print("Sorting is not supported on an unaggregated stream")

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.0. Writing a Stream
# MAGIC The method `DataFrame.writeStream` returns a `DataStreamWriter` that is used to configure the output of a stream.
# MAGIC 
# MAGIC There are a number of parameters to the `DataStreamWriter` configuration:
# MAGIC * Query's name (optional) - This name must be unique among all the currently active queries in the associated SQLContext.
# MAGIC * Trigger (optional) - Default value is `ProcessingTime(0`) and it will run the query as fast as possible.
# MAGIC * Checkpointing directory (optional)
# MAGIC * Output mode
# MAGIC * Output sink
# MAGIC * Configuration specific to the output sink, such as:
# MAGIC   * The host, port and topic of the receiving Kafka server
# MAGIC   * The file format and final destination of files
# MAGIC   * A custom sink via `dsw.foreach(...)`
# MAGIC 
# MAGIC Once the configuration is completed, the job can be triggered by calling `dsw.start()`
# MAGIC 
# MAGIC ##### 2.1. Triggers
# MAGIC The trigger specifies when the system should process the next set of data.
# MAGIC 
# MAGIC | Trigger Type                           | Example | Notes |
# MAGIC |----------------------------------------|-----------|-------------|
# MAGIC | Unspecified                            |  | _DEFAULT_- The query will be executed as soon as the system has completed processing the previous query |
# MAGIC | Fixed interval micro-batches           | `dsw.trigger(Trigger.ProcessingTime("6 hours"))` | The query will be executed in micro-batches and kicked off at the user-specified intervals |
# MAGIC | One-time micro-batch                   | `dsw.trigger(Trigger.Once())` | The query will execute _only one_ micro-batch to process all the available data and then stop on its own |
# MAGIC | Continuous w/fixed checkpoint interval | `dsw.trigger(Trigger.Continuous("1 second"))` | The query will be executed in a low-latency, continuous processing mode. _EXPERIMENTAL_ in 2.3.2 |
# MAGIC 
# MAGIC The following illustrates configuring a fixed interval of 3 seconds:<br>
# MAGIC `dsw.trigger(Trigger.ProcessingTime("3 seconds"))`
# MAGIC 
# MAGIC 
# MAGIC ##### 2.2. Checkpointing
# MAGIC A **checkpoint** stores the current state of a streaming job to a reliable storage system such as Amazon S3, Azure Data Lake Storage (ADLS), or Hadoop Distributed File System (HDFS). It does not store the state of your streaming job to the local file system of any node in your cluster. Together with write ahead logs, a terminated stream can be restarted, and it will continue from where it left off.
# MAGIC To enable this feature, you only need to specify the location of a checkpoint directory: `dsw.option("checkpointLocation", checkpointPath)`
# MAGIC 
# MAGIC Points to consider:
# MAGIC * If you do not have a checkpoint directory, when the streaming job stops, you will lose all state regarding the streaming job... and upon restart, you start from scratch.
# MAGIC * For some sinks, you will get an error if you do not specify a checkpoint directory (e.g.,`analysisException: 'checkpointLocation must be specified either through option("checkpointLocation", ...)..`)
# MAGIC * Each streaming job requires a dedicated checkpoint directory (i.e., streaming jobs cannot share checkpoint direcctories).
# MAGIC 
# MAGIC 
# MAGIC ##### 2.3. Output Modes
# MAGIC 
# MAGIC | Mode   | Example | Notes |
# MAGIC | ------------- | ----------- |
# MAGIC | **Complete** | `dsw.outputMode("complete")` | The entire updated Result Table is written to the sink. The individual sink implementation decides how to handle writing the entire table. |
# MAGIC | **Append** | `dsw.outputMode("append")`     | Only the new rows appended to the Result Table since the last trigger are written to the sink. |
# MAGIC | **Update** | `dsw.outputMode("update")`     | Only the rows in the Result Table that were updated since the last trigger will be outputted to the sink. Since Spark 2.1.1 |
# MAGIC 
# MAGIC The following example illustrates writing to a Parquet directory that only supports the `append` mode: `dsw.outputMode("append")`
# MAGIC 
# MAGIC 
# MAGIC ##### 2.4. Output Sinks
# MAGIC 
# MAGIC `DataStreamWriter.format` accepts the following values, among others:
# MAGIC 
# MAGIC | Output Sink | Example                                          | Notes |
# MAGIC | ----------- | ------------------------------------------------ | ----- |
# MAGIC | **File**    | `dsw.format("parquet")`, `dsw.format("csv")`...  | Dumps the Result Table to a file. Supports Parquet, json, csv, etc.|
# MAGIC | **Kafka**   | `dsw.format("kafka")`      | Writes the output to one or more topics in Kafka |
# MAGIC | **Console** | `dsw.format("console")`    | Prints data to the console (useful for debugging) |
# MAGIC | **Memory**  | `dsw.format("memory")`     | Updates an in-memory table, which can be queried through Spark SQL or the DataFrame API |
# MAGIC | **foreach** | `dsw.foreach(writer: ForeachWriter)` | This is your "escape hatch", allowing you to write your own type of sink. |
# MAGIC | **Delta**    | `dsw.format("delta")`     | A proprietary sink |
# MAGIC 
# MAGIC The follwing example illustrates appending files to a Parquet file while specifying its location: `dsw.format("parquet").start(outputPathDir)`
# MAGIC 
# MAGIC 
# MAGIC ##### 2.5. Starting a Stream
# MAGIC The cells below demonstrate writting data from a streaming query to `outputPathDir`. 
# MAGIC 
# MAGIC A couple of things to note below:
# MAGIC - The query is being named via the call to `queryName`... which can be used later to reference the query by name.
# MAGIC - Spark begins running jobs once the call to `start` is made... which is the equivalent of calling an action on a "static" DataFrame.
# MAGIC - The call to `start` returns a `StreamingQuery` object... which can be used to interact with the running query.

# COMMAND ----------

outputPathDir = workingDir + "/output.parquet" # A subdirectory for our output
checkpointPath = workingDir + "/checkpoint"    # A subdirectory for our checkpoint & W-A logs
streamName = "lesson01_ps"                     # An arbitrary name for the stream

# COMMAND ----------

streamingQuery = (streamingDF                   # Start with our "streaming" DataFrame
  .writeStream                                  # Get the DataStreamWriter
  .queryName(streamName)                        # Name the query
  .trigger(processingTime="3 seconds")          # Configure for a 3-second micro-batch
  .format("parquet")                            # Specify the sink type, a Parquet file
  .option("checkpointLocation", checkpointPath) # Specify the location of checkpoint files & W-A logs
  .outputMode("append")                         # Write only new data to the "file"
  .start(outputPathDir)                         # Start the job, writing to the specified directory
)

# COMMAND ----------

untilStreamIsReady(streamName)                  # Wait until stream is done initializing...

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.0. Managing Streaming Queries
# MAGIC 
# MAGIC When a query is started, the `StreamingQuery` object can be used to monitor and manage the query.
# MAGIC 
# MAGIC | Method    |  Description |
# MAGIC | ----------- | ------------------------------- |
# MAGIC |`id`| get unique identifier of the running query that persists across restarts from checkpoint data |
# MAGIC |`runId`| get unique id of this run of the query, which will be generated at every start/restart |
# MAGIC |`name`| get name of the auto-generated or user-specified name |
# MAGIC |`explain()`| print detailed explanations of the query |
# MAGIC |`stop()`| stop query |
# MAGIC |`awaitTermination()`| block until query is terminated, with stop() or with error |
# MAGIC |`exception`| exception if query terminated with error |
# MAGIC |`recentProgress`| array of most recent progress updates for this query |
# MAGIC |`lastProgress`| most recent progress update of this streaming query |
# MAGIC 
# MAGIC For example, the following cell demonstrates polling the streaming query for its most recent progress!

# COMMAND ----------

streamingQuery.recentProgress                   # Poll the streaming query for its most recent progress

# COMMAND ----------

# MAGIC %md
# MAGIC The following example demonstrates how to discover all actively running streams:

# COMMAND ----------

for s in spark.streams.active:                  # Iterate over all streams
  print("{}: {}".format(s.id, s.name))          # Print the stream's id and name

# COMMAND ----------

# MAGIC %md
# MAGIC The following example demonstrates **`awaitTermination()`** which blocks the current thread:
# MAGIC * Until the stream stops naturally, or... 
# MAGIC * Until the specified timeout elapses (if specified)
# MAGIC 
# MAGIC If the stream was "canceled", or otherwise terminated abnormally, any resulting exceptions will be thrown by **`awaitTermination()`** as well.

# COMMAND ----------

try:
    streamingQuery.awaitTermination(10)         # Stream for up to 10 seconds while the current thread blocks
    print("Awaiting Termination...")
  
except Exception as e:
  print(e)

# COMMAND ----------

# MAGIC %md
# MAGIC ... And once the 10 seconds have elapsed without any error, we can explictly stop the stream.

# COMMAND ----------

try:
  streamingQuery.stop()                         # Issue the command to stop the stream
  print("The stream has been stopped!")

except Exception:
  print(e)

# COMMAND ----------

# MAGIC %md
# MAGIC When working with streams, in reality, we are working with a separate *thread* of execution. As a result, different exceptions may arise as streams are terminated and/or queried.
# MAGIC 
# MAGIC For this reason, we have developed a number of utility methods to help with these operations:
# MAGIC * **`untilStreamIsReady(name)`** to wait until a stream is fully initialized before resuming execution.
# MAGIC * **`stopAllStreams()`** to stop all active streams in a fail-safe manner.
# MAGIC 
# MAGIC The implementation of each of these can be found in the notebook **`./Includes/Common-Notebooks/Utility-Methods`**
# MAGIC <br><br>
# MAGIC 
# MAGIC #### 4.0. The Display Function
# MAGIC Within Databricks notebooks we can use the `display()` function to render a live plot; **however...**
# MAGIC 
# MAGIC When you pass a "streaming" `DataFrame` to `display`:
# MAGIC * A "memory" sink is being used
# MAGIC * The output mode is complete
# MAGIC * The query name is specified with the `streamName` parameter
# MAGIC * The trigger is specified with the `trigger` parameter
# MAGIC * The checkpointing location is specified with the `checkpointLocation`
# MAGIC 
# MAGIC `display(myDF, streamName = "myQuery")`
# MAGIC 
# MAGIC Because the only active streaming query was programmatically stopped in the previous cell, we will now call `display` in the following cell to *automatically* start the streaming DataFrame, `streamingDF`. This also affords the opportunity for passing `stream_2p` as a new **name** for this newly started stream.

# COMMAND ----------

newStreamName = 'stream_2p'
display(streamingDF, streamName = newStreamName)

# COMMAND ----------

untilStreamIsReady(newStreamName)               # Wait until stream is done initializing...

# COMMAND ----------

# MAGIC %md
# MAGIC The cell below demonstrates how the value passed to `streamName` in the call to `display` enables programatic access the specific stream:

# COMMAND ----------

print("Looking for {}".format(newStreamName))

for stream in spark.streams.active:             # Loop over all active streams
  if stream.name == newStreamName:              # Single out "stream_2p"
    print("Found {} ({})".format(stream.name, stream.id)) 

# COMMAND ----------

# MAGIC %md
# MAGIC ...And finally, all streams can be stopped by calling the `stopAllStreams()` function:

# COMMAND ----------

stopAllStreams()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 5.0. Summary
# MAGIC Use cases for streaming include bank card transactions, log files, Internet of Things (IoT) device data, video game play events and countless others.
# MAGIC 
# MAGIC Some key properties of streaming data include:
# MAGIC * Data coming from a stream is typically not ordered in any way
# MAGIC * The data is streamed into a **data lake**
# MAGIC * The data is coming in faster than it can be consumed
# MAGIC * Streams are often chained together to form a data pipeline
# MAGIC * Streams don't have to run 24/7:
# MAGIC   * Consider the new log files that are processed once an hour
# MAGIC   * Or the financial statement that is processed once a month
# MAGIC   
# MAGIC `readStream` is used to read streaming input from a variety of input sources, and to create a DataFrame.
# MAGIC Nothing happens until either `writeStream` or `display` is invoked. 
# MAGIC `writeStream` can be used to write data to a variety of output sinks.
# MAGIC `display` can be used to draw LIVE bar graphs, charts and other plot types in the notebook.
# MAGIC 
# MAGIC <br>
# MAGIC 
# MAGIC **Run the following cell to delete the tables, files, and any other artifacts associated with this lesson.**

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Cleanup

# COMMAND ----------

# MAGIC %md
# MAGIC #### 6.0. Review Questions
# MAGIC 
# MAGIC **Question:** What is Structured Streaming?<br>
# MAGIC **Answer:** A stream is a sequence of data that is made available over time.<br>
# MAGIC Structured Streaming where we treat a <b>stream</b> of data as a table to which data is continously appended.<br>
# MAGIC The developer then defines a query on this input table, as if it were a static table, to compute a final result table that will be written to an output <b>sink</b>. 
# MAGIC 
# MAGIC **Question:** What purpose do triggers serve?<br>
# MAGIC **Answer:** Developers define triggers to control how frequently the input table is updated.
# MAGIC 
# MAGIC **Question:** How does micro batch work?<br>
# MAGIC **Answer:** We take our firehose of data and collect data for a set interval of time (the Trigger Interval).<br>
# MAGIC For each interval, our job is to process the data from the previous time interval.<br>
# MAGIC As we are processing data, the next batch of data is being collected for us.
# MAGIC 
# MAGIC **Q:** What do `readStream` and `writeStream` do?<br>
# MAGIC **A:** `readStream` creates a streaming DataFrame.  `writeStream` sends streaming data to a directory or other type of output sink.
# MAGIC 
# MAGIC **Q:** What does `display` output if it is applied to a DataFrame created via `readStream`?<br>
# MAGIC **A:** `display` sends streaming data to a LIVE graph!
# MAGIC 
# MAGIC **Q:** When you do a write stream command, what does this option do `outputMode("append")` ?<br>
# MAGIC **A:** This option takes on the following values and their respective meanings:
# MAGIC * <b>append</b>: add only new records to output sink
# MAGIC * <b>complete</b>: rewrite full output - applicable to aggregations operations
# MAGIC * <b>update</b>: update changed records in place
# MAGIC 
# MAGIC **Q:** What happens if you do not specify `option("checkpointLocation", pointer-to-checkpoint directory)`?<br>
# MAGIC **A:** When the streaming job stops, you lose all state around your streaming job and upon restart, you start from scratch.
# MAGIC 
# MAGIC **Q:** How do you view the list of active streams?<br>
# MAGIC **A:** Invoke `spark.streams.active`.
# MAGIC 
# MAGIC **Q:** How do you verify whether `streamingQuery` is running (boolean output)?<br>
# MAGIC **A:** Invoke `spark.streams.get(streamingQuery.id).isActive`.