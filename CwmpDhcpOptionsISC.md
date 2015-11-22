# CWMP DHCP Option Handling #

CPE devices are often hard-coded with the ACS URL to use, making the device specific to a particular network (and sometimes even a specific geographical area). The CWMP spec describes how to instead use DHCP vendor options to supply the device with an ACS URL, in section 3.1 of TR-69 Amendment 3.

Catawampus does not implement a DHCP client directly, as that would be silly, but is designed to accept configuration from a DHCP client.

## ISC DHCP client ##

This page describes how to configure the [ISC DHCP client](http://www.isc.org/software/dhcp) to fetch CWMP options and pass them to catawampus.

### DHCP4 ###
TBD.

### DHCP6 ###

DHCP6 uses Vendor-Identifying Vendor Options (VIVO). The client must populate a vendor-class option containing the string "dslforum.org", which tells the DHCP server to supply the CWMP vendor options. An example /etc/dhclient6.conf:

```
script "/sbin/dhclient-script";

option space cwmp code width 2 length width 2;
option cwmp.acs-url code 1 = text;
option cwmp.provisioning-code code 2 = text;
option cwmp.retry-minimum-wait-interval code 3 = text;
option cwmp.retry-interval-multiplier code 4 = text;
option vsio.cwmp code 3561 = encapsulate cwmp;

option dhcp6.vendor-class code 16 = {integer 32, integer 16, string};
interface "br0" {
    # vendor = 3561 (Broadband Forum), len = 12, content = dslforum.org
    send dhcp6.vendor-class 3561 12 "dslforum.org";
    also request dhcp6.fqdn, dhcp6.sntp-servers, dhcp6.vendor-opts;
}
```


### dhclient-script ###

The dhclient config scripts specify how to parse the vendor options out of the DHCP packet. dhclient will then run /sbin/dhclient-script (specified in the "script" statement above) with environment variables set for each DHCP option. It is the responsibility of the script to apply those options however the platform requires.

Catawampus has command line arguments to specify filename where it should retrieve each parameter. Catawampus rereads the file each time it needs it, so if a subsequent DHCP renewal changes the value it will be picked up at the next opportunity.

Most Linux distributions come with an /sbin/dhclient-script. Here is the handling which should be added:

```
make_cwmp_files() {
  mkdir /tmp/cwmp
  if [ "x${new_cwmp_acs_url}" != x ] ; then
    echo ${new_cwmp_acs_url} > /tmp/cwmp/acs_url
  fi
  if [ "x${new_cwmp_provisioning_code}" != x ] ; then
    echo ${new_cwmp_provisioning_code} > /tmp/cwmp/provisioning_code
  fi
  if [ "x${new_cwmp_retry_minimum_wait_interval}" != x ] ; then
    echo ${new_cwmp_retry_minimum_wait_interval} > /tmp/cwmp/retry_minimum_wait_interval
  fi
  if [ "x${new_cwmp_retry_interval_multiplier}" != x ] ; then
    echo ${new_cwmp_retry_interval_multiplier} > /tmp/cwmp/retry_interval_multiplier
  fi
}

if [ x$reason = xBOUND ] || [ x$reason = xRENEW ] || \
   [ x$reason = xREBIND ] || [ x$reason = xREBOOT ]; then
  # ... handling for IP address, nameservers, etc...

  make_cwmp_files
}

if [ x$reason = xBOUND6 ] ; then
  #... handling for the IP6 address...

  make_cwmp_files
}

if [ x$reason = xRENEW6 ] || [ x$reason = xREBIND6 ] ; then
  #...handling for nameservers, domain name, etc...

  if [ "x${new_cwmp_acs_url}" != "x${old_cwmp_acs_url}" ] ||
     [ "x${new_cwmp_provisioning_code}" != "x${old_cwmp_provisioning_code}" ] ||
     [ "x${new_cwmp_retry_minimum_wait_interval}" != "x${old_cwmp_retry_minimum_wait_interval}" ] ||
     [ "x${new_cwmp_retry_interval_multiplier}" != "x${old_cwmp_retry_interval_multiplier}" ] ; then
    make_cwmp_files
  fi
}

```


### Passing options to the agent ###

The dhclient.conf specified how to request and parse the CWMP options, and the dhclient-script placed the content of those options into files in /tmp/cwmp. Now we need to tell catawampus how to find them.

At the time of this writing (2/2012) catawampus only implements support for the ACS-URL option, by passing the name of the file which dhclient-scipt will write to:

`python runserver.py --acs-url-file=/tmp/cwmp/acs_url ...`