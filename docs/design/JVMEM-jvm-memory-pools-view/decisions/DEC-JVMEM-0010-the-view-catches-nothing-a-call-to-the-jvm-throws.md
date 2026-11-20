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
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0009](DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md), [PRINCIPLE-036](../../../process/principles.md#principle-036), [PRINCIPLE-054](../../../process/principles.md#principle-054), [PRINCIPLE-078](../../../process/principles.md#principle-078) |
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

What Apache Cassandra does with what a statement throws was read in the code. All of it is ChronitonDB chronitondb-sandbox at `ffa1bc742d`, unchanged against the base of the line, Apache Cassandra cassandra-5.0 at `76550e9314`. Section 12 of the feature spec has the lines in Apache Cassandra now, where the code does the same.

1. An exception that escapes a statement a client sends is caught by the message that carries the statement: `QueryMessage.execute`, `src/java/org/apache/cassandra/transport/messages/QueryMessage.java:102`, the catch at line 125, and `ExecuteMessage.execute`, `src/java/org/apache/cassandra/transport/messages/ExecuteMessage.java:131`, the catch at line 205.
2. An exception that is none of the request errors of Apache Cassandra is logged at ERROR and answered with a server error that carries the text of the exception: `ErrorMessage.fromException`, `src/java/org/apache/cassandra/transport/messages/ErrorMessage.java:437`, the log line at 473 and the server error at 475, and `ServerError.ServerError`, `src/java/org/apache/cassandra/transport/ServerError.java:28`.
3. An out of memory error is logged and thrown on for the JVM to handle: `JVMStabilityInspector.inspectThrowable`, `src/java/org/apache/cassandra/utils/JVMStabilityInspector.java:105`, the log line at 123 and the throw at line 131. An error of the JVM is no exception, so it passes the catches of item 1 and is caught where the request is dispatched, which gives it to that method: `Dispatcher.processRequest`, `src/java/org/apache/cassandra/transport/Dispatcher.java:429`, the catch at line 436.

No case is known in which a JVM makes one of the view's calls throw an exception, and none was looked for. What a statement answered from more than one read returns when one of its reads fails was not read in the code.

## Considered options

1. The view catches nothing. What a call throws goes to Apache Cassandra's own handling, for the call for the list of pools too.
2. The view catches an exception of any of its calls and fails the read with an error of its own, with a class and a text the feature defines. An out of memory error still goes to the JVM.

## Decision outcome

Chosen option: "The view catches nothing", because it adds no code and no error of the feature's own, and the operator still sees the failure, at the client and in the log. Option 2 adds an error to define, document and test, for a failure that no JVM is known to cause. That is more than the need asks for ([PRINCIPLE-054](../../../process/principles.md#principle-054)).

1. The view MUST NOT catch what a call it makes to the JVM throws while a read builds its rows. That holds for the call for the list of memory pools as for a call to the bean of one pool, and for an error of the JVM as for an exception.
2. The feature MUST NOT change what Apache Cassandra does with what was thrown.
3. The documentation of the view MUST say that the view passes on what a call to the JVM throws, and what Apache Cassandra then answers and logs, as the context above states it.

The ERROR line is that of an unexpected error of the server, which [PRINCIPLE-036](../../../process/principles.md#principle-036) lets a node log for each failing request. The view has no expected failure of its own: a memory pool whose usage the JVM does not report is a row and no error. The error is unexpected because no JVM is known to raise it. It is logged for each read that fails, so its rate is the rate at which roles that may read the view read it while the error lasts, and the feature adds no other bound. The line holds the exception and no user data.

### Consequences

- Good: the view adds no error handling, so nothing of the feature can hide an error of the JVM or change how the node treats one.
- Good: an out of memory error during a read of the view is handled as on any other request.
- Bad: a client gets a server error with the text of a Java exception, which is no text the feature wrote for an operator.
- Bad: a tool that polls the view adds ERROR lines to the log of the node while the error lasts.
- Neutral: what a statement answered from more than one read returns when one of its reads fails is left to the design record of the item, which reads it in the code.

## More information

- The [feature spec](../feature-spec.md), section 2.5 for errors, section 3 for the requirements and section 12 for the code facts.
