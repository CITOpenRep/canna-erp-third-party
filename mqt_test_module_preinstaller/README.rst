.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
MQT Test Module Preinstaller
============================

Define modules which should be preinstalled in the dependency list of
this module.
The motivation for this module is that in the __init__.py of the account
module some extra modules are installed depending on which l10n_* where * is
the country code are installed. In the case of the third-party repo
l10n_be_coa_multilang among some others are installed.
The account module expects a CoA to be configured by this kind of module,
however these l10n_be_* modules depend on a CoA to be imported and do not
specify one themselves.
By adding a module which is not depended on and not auto-installed when setting
up a normal instance, but is installed by the MQT-test suite simply because it
is part of the repo (and hence should be tested), and having a dependency on
l10n_generic_coa, we accommodate the other third-party modules which tests
depend on a CoA being installed.
