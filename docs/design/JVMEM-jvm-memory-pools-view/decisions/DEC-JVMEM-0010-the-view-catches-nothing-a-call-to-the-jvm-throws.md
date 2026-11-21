<!--
Copyright 2026 AxonOps Limited
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# DEC-JVMEM-0010. The view catches nothing that a call to the JVM throws

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0006](DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md), [DEC-JVMEM-0009](DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md), [PRINCIPLE-036](../../../process/principles.md#principle-036), [PRINCIPLE-054](../../../process/principles.md#principle-054), [PRINCIPLE-059](../../../process/principles.md#principle-059), [PRINCIPLE-078](../../../process/principles.md#principle-078) |
| Areas | observability |
| Supersedes | None |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The view builds its rows by calls to the JVM: one call for the list of memory pools, and calls to each pool's bean. [DEC-JVMEM-0009](DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md) settled that a read fails when such a call throws. It had to be settled what the view does with what was thrown: which error a client gets, what the node logs, whether the call for the list counts, and what happens to an error of the JVM such as an out of memory error.

What Apache Cassandra does with what a statement throws was read in the code, and each claim names the code it was read in ([PRINCIPLE-078](../../../process/principles.md#principle-078)). All of it is ChronitonDB chronitondb-sandbox at `ffa1bc742d`, unchanged against the base of the line, Apache Cassandra cassandra-5.0 at `76550e9314`. The nine files cited below are the same in Apache Cassandra cassandra-5.0 at `47227d98bf`. Section 12 of the feature spec has the lines in Apache Cassandra now, where the code does the same.

1. An exception that escapes a statement a client sends is caught by the message that carries the statement: `QueryMessage.execute`, `src/java/org/apache/cassandra/transport/messages/QueryMessage.java:102`, the catch at line 125, and `ExecuteMessage.execute`, `src/java/org/apache/cassandra/transport/messages/ExecuteMessage.java:131`, the catch at line 205.
2. An exception that is none of the request errors of Apache Cassandra is answered with a server error whose message is the `toString` of the exception, which is its class name and its message, and it is logged at ERROR where that error is made: `ErrorMessage.fromException`, `src/java/org/apache/cassandra/transport/messages/ErrorMessage.java:437`, the log line at 473 and the server error at 475, and `ServerError.ServerError`, `src/java/org/apache/cassandra/transport/ServerError.java:28`, the `toString` at line 30. `QueryMessage.execute` logs the exception at ERROR once more, at line 130, before it asks for that error, and `ExecuteMessage.execute` has no log line of its own. Each of those log calls is given the exception, so each entry carries its stack trace. So a statement that a client sends as text, as `cqlsh` does, writes two ERROR entries, and a prepared statement writes one.
3. An out of memory error is logged at ERROR with its stack trace, and an error is then thrown on for the JVM to handle: `JVMStabilityInspector.inspectThrowable`, `src/java/org/apache/cassandra/utils/JVMStabilityInspector.java:105`, the log line at 123 and the throw at line 131. Where the message of the error is `Java heap space` or `GC Overhead limit exceeded`, the error thrown on is that error. For any other message it is logged in a second ERROR entry with its stack trace, and the heap is then filled until an allocation throws an out of memory error, which goes on in its place: `JVMStabilityInspector.forceHeapSpaceOomMaybe`, `src/java/org/apache/cassandra/utils/JVMStabilityInspector.java:193`, called at line 127, the two texts at line 184, the ERROR line at 197 and the loop at 200. Where the system property `cassandra.printHeapHistogramOnOutOfMemoryError` is on, all of that holds only for the first out of memory error that Apache Cassandra's handling meets on the node, and a heap histogram is logged before its first ERROR entry: an INFO line, then the output of `jcmd` with `GC.class_histogram` in one INFO entry, or an ERROR entry where the process id cannot be found or the attempt throws. The call is at line 120 of `JVMStabilityInspector.inspectThrowable`, and the lines are those of `HeapUtils.logHeapHistogram`, `src/java/org/apache/cassandra/utils/HeapUtils.java:57`, the INFO line at 61, the ERROR lines at 66 and 83 and the command at 79, and of `HeapUtils.logProcessOutput`, `src/java/org/apache/cassandra/utils/HeapUtils.java:171`, the INFO entry at 181. A later out of memory error is neither logged there nor thrown on, and it is answered and logged as another error of the JVM is. The method checks the property at line 110 and returns at line 117 once a flag is set that the first such error sets and nothing clears. An error of the JVM is no exception, so it passes the catches of item 1 and is caught where the request is dispatched, which gives it to that method: `Dispatcher.processRequest`, `src/java/org/apache/cassandra/transport/Dispatcher.java:429`, the catch at line 436. An error of the JVM that is no out of memory error is then answered with the server error of item 2 and logged once, by the handler of the client's channel, at ERROR, or at DEBUG where the address of the client lies in a subnet that the setting `client_error_reporting_exclusions` lists: the handler at line 443 and the server error at 444 of that method, `ExceptionHandlers.getUnexpectedExceptionHandler`, `src/java/org/apache/cassandra/transport/ExceptionHandlers.java:185`, the DEBUG line at 191, `SubnetGroups.contains`, `src/java/org/apache/cassandra/config/SubnetGroups.java:57`, and `ExceptionHandlers.UnexpectedChannelExceptionHandler.apply`, `src/java/org/apache/cassandra/transport/ExceptionHandlers.java:227`, the ERROR line at 271.

No case is known in which a JVM makes one of the view's calls throw an exception, and none was looked for. What a statement answered from more than one read returns when one of its reads fails was not read in the code.

It also had to be settled whether the feature spec and the documentation name the code in which Apache Cassandra's answer and its log lines were read. No test of the feature covers that code, so an import from Apache Cassandra can change it with no test failing. [DEC-JVMEM-0006](DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md) settled the same question for a grant left behind: the text names the three commits that were read.

## Considered options

1. The view catches nothing. What a call throws goes to Apache Cassandra's own handling, for the call for the list of pools too.
2. The view catches an exception of any of its calls and fails the read with an error of its own, with a class and a text the feature defines. An out of memory error still goes to the JVM.

For how the text states what Apache Cassandra answers and logs, two options were considered: with the three commits in whose code it was read, or as a fact with no commit.

## Decision outcome

Chosen option: "The view catches nothing", because it adds no code and no error of the feature's own, and the operator still sees the failure, at the client and in the log. Option 2 adds an error to define, document and test, for a failure that no JVM is known to cause. That is more than the need asks for ([PRINCIPLE-054](../../../process/principles.md#principle-054)).

1. The view MUST NOT catch what a call it makes to the JVM throws while a read builds its rows. That holds for the call for the list of memory pools as for a call to the bean of one pool, and for an error of the JVM as for an exception.
2. The feature MUST NOT change what Apache Cassandra does with what was thrown.
3. The documentation of the view MUST say that the view passes on what a call to the JVM throws, and what Apache Cassandra then answers and logs, as the context above states it.
4. The feature spec and the documentation MUST say what Apache Cassandra answers and logs for the code that was read, and name that code by its three commits: ChronitonDB chronitondb-sandbox at `ffa1bc742d`, Apache Cassandra cassandra-5.0 at `76550e9314` and Apache Cassandra cassandra-5.0 at `47227d98bf`.
5. The feature spec and the documentation MUST say that they make that statement for no other code. A release of the line and another release of Apache Cassandra are other code.

Items 4 and 5 are chosen because a claim about code names the code it was read in ([PRINCIPLE-078](../../../process/principles.md#principle-078)), and because [DEC-JVMEM-0006](DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md) names the commits for the same kind of statement ([PRINCIPLE-059](../../../process/principles.md#principle-059)). A statement with no commit is plainer to read, and an import that changes that code would make it wrong with no test failing.

The ERROR entries are those of an unexpected error of the server, which [PRINCIPLE-036](../../../process/principles.md#principle-036) lets a node log for each failing request. The view has no expected failure of its own: a memory pool whose usage the JVM does not report is a row and no error. The failure is unexpected because no case is known in which a JVM makes a call of the view throw an exception. An out of memory error is another kind of failure, since any call that needs memory can throw one while the heap is full. The entries are logged for each request of a client that fails, so their rate is the rate at which clients send such requests while the fault lasts, and the feature adds no other bound. Each holds what was thrown, with its stack trace, and no user data.

### Consequences

- Good: the view adds no error handling, so nothing of the feature can hide an error of the JVM or change how the node treats one.
- Good: an out of memory error during a read of the view is handled as on any other request.
- Bad: a client gets a server error with the class name and the message of a Java exception, which is no text the feature wrote for an operator.
- Bad: a tool that polls the view adds ERROR lines to the log of the node while the error lasts.
- Bad: the documentation names commits and no release for what Apache Cassandra answers and logs, so an operator cannot match that statement to a release by name.
- Bad: after an import from Apache Cassandra changes that code, the documentation still says only what was read in the three commits.
- Neutral: what a statement answered from more than one read returns when one of its reads fails is left to the design record of the item, which reads it in the code.

## More information

- The [feature spec](../feature-spec.md), section 2.5 for errors, section 3 for the requirements and section 12 for the code facts.
