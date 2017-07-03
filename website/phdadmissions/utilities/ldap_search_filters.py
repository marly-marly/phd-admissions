from django_python3_ldap.utils import format_search_filters


# DoC Staff members only
def doc_staff_search_filter(ldap_fields):
    # memberOf=CN=doc-staff,OU=Distribution,OU=Groups,OU=Imperial College (London),DC=ic,DC=ac,DC=uk
    ldap_fields["memberOf"] = "CN=doc-teaching-list,OU=Distribution,OU=Groups,OU=Imperial College (London),DC=ic,DC=ac,DC=uk"
    search_filters = format_search_filters(ldap_fields)

    return search_filters
