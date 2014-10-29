RAW_NODES = '''<nodecomponent_manager_id="urn:publicID:ThisisaURNof0"component_name="urn:publicID:ThisisaURNof0"component_id="urn:publicID:ThisisaURNof0"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof1"component_name="urn:publicID:ThisisaURNof1"component_id="urn:publicID:ThisisaURNof1"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof2"component_name="urn:publicID:ThisisaURNof2"component_id="urn:publicID:ThisisaURNof2"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof3"component_name="urn:publicID:ThisisaURNof3"component_id="urn:publicID:ThisisaURNof3"exclusive="true"><availablenow="none"/></node>'''
                  
AD_RSPEC = '''<?xmlversion="1.0"encoding="UTF-8"?><rspecxmlns="http://www.geni.net/resources/rspec/3"xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://www.geni.net/resources/rspec/3http://www.geni.net/resources/rspec/3/ad.xsd"type="advertisement"><nodecomponent_manager_id="urn:publicID:ThisisaURNof0"component_name="urn:publicID:ThisisaURNof0"component_id="urn:publicID:ThisisaURNof0"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof1"component_name="urn:publicID:ThisisaURNof1"component_id="urn:publicID:ThisisaURNof1"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof2"component_name="urn:publicID:ThisisaURNof2"component_id="urn:publicID:ThisisaURNof2"exclusive="true"><availablenow="none"/></node><nodecomponent_manager_id="urn:publicID:ThisisaURNof3"component_name="urn:publicID:ThisisaURNof3"component_id="urn:publicID:ThisisaURNof3"exclusive="true"><availablenow="none"/></node></rspec>'''
               
RAW_MANIFEST = '''<nodeclient_id="None"component_id="urn:publicID:ResourceURN0"component_manager_id="urn:publicID:ResourceURN0"sliver_id="urn:publicID:Sliver0"></node><nodeclient_id="None"component_id="urn:publicID:ResourceURN1"component_manager_id="urn:publicID:ResourceURN1"sliver_id="urn:publicID:Sliver1"></node><nodeclient_id="None"component_id="urn:publicID:ResourceURN2"component_manager_id="urn:publicID:ResourceURN2"sliver_id="urn:publicID:Sliver2"></node>'''
                        
FULL_MANIFEST = '''<?xmlversion="1.0"encoding="UTF-8"?><rspecxmlns="http://www.geni.net/resources/rspec/3"xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://www.geni.net/resources/rspec/3http://www.geni.net/resources/rspec/3/manifest.xsd"type="manifest"><nodeclient_id="None"component_id="urn:publicID:ResourceURN0"component_manager_id="urn:publicID:ResourceURN0"sliver_id="urn:publicID:Sliver0"></node><nodeclient_id="None"component_id="urn:publicID:ResourceURN1"component_manager_id="urn:publicID:ResourceURN1"sliver_id="urn:publicID:Sliver1"></node><nodeclient_id="None"component_id="urn:publicID:ResourceURN2"component_manager_id="urn:publicID:ResourceURN2"sliver_id="urn:publicID:Sliver2"></node></rspec>'''

REQUEST_EXAMPLE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rspec generated="2014-03-22T01:53:21.460+01:00" generated_by="Experimental jFed Rspec Editor" type="request" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd" xmlns="http://www.geni.net/resources/rspec/3" xmlns:jFed="http://jfed.iminds.be/rspec/ext/jfed/1" xmlns:jFedBonfire="http://jfed.iminds.be/rspec/ext/jfed-bonfire/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:emulab="http://www.protogeni.net/resources/rspec/ext/emulab/1">
  <node client_id="node0" component_id="urn:publicid:IDN+wall2.ilabt.iminds.be+node+n095-01a" component_manager_id="urn:publicid:IDN+wall2.ilabt.iminds.be+authority+cm" exclusive="true">
      <sliver_type name="emulab-xen">
        <emulab:xen cores="10" ram="8192" disk="50"/>
        <disk_image name="urn:publicid:IDN+wall2.ilabt.iminds.be+image+emulab-ops//DEB60_64-VLAN"/>
     </sliver_type>
  </node>
</rspec>'''

ALL_LINKS = '''<?xmlversion="1.0"encoding="UTF-8"?><rspecxmlns="http://www.geni.net/resources/rspec/3"xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://www.geni.net/resources/rspec/3http://www.geni.net/resources/rspec/3/ad.xsd"type="advertisement"><linkcomponent_id="urn:publicID:ThisisaURNofLINK0"component_name="urn:publicID:ThisisaURNofLINK0"><propertysource_id="A"dest_id="B"capacity="10thousandTrillions"/><link_typename="HighQualityL2Link"/></link><linkcomponent_id="urn:publicID:ThisisaURNofLINK1"component_name="urn:publicID:ThisisaURNofLINK1"><propertysource_id="A"dest_id="B"capacity="10thousandTrillions"/><link_typename="HighQualityL2Link"/></link><linkcomponent_id="urn:publicID:ThisisaURNofLINK2"component_name="urn:publicID:ThisisaURNofLINK2"><propertysource_id="A"dest_id="B"capacity="10thousandTrillions"/><link_typename="HighQualityL2Link"/></link><linkcomponent_id="urn:publicID:ThisisaURNofLINK3"component_name="urn:publicID:ThisisaURNofLINK3"><propertysource_id="A"dest_id="B"capacity="10thousandTrillions"/><link_typename="HighQualityL2Link"/></link></rspec>'''
SINGLE_LINK = '''<linkcomponent_id="urn:publicID:ThisisaURNofLINK0"component_name="urn:publicID:ThisisaURNofLINK0"><propertysource_id="A"dest_id="B"capacity="10thousandTrillions"/><link_typename="HighQualityL2Link"/></link>'''

LINK_REQUEST = '''<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd"
       type="advertisement">
  <link component_id="urn:publicid:aist-se1-dp1" component_name="link-pc111:eth0-cisco3:(null)">
    <property source_id="Verdaguer" dest_id="dpid5" capacity="*"/>
    <link_type name="urn:ocf+static_link"/>
  </link>
</rspec>'''

