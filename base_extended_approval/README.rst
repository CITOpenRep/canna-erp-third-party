Base Extended Approval
======================

This module provides the base for extended approval flows. Through addon modules
extended flows can be made available for models.

When a model has an extended approval flow, when an object enters the approval
process the first matching flow (for which the domain applies) is used for the
approval process.

Each step of the flow for which the condition applies has to be completed. It
can be completed by a user which has any of the groups mentioned.

The applicable steps will be completed in sequence, and for each step a log
record will be created.

If a user belongs to the groups of multiple consecutive steps, all these steps
will be completed at once.
