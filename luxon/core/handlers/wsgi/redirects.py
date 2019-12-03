# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.


class Redirects(object):
    __slots__ = ()

    def redirect_permanently(self, location):
        """ 301 Moved Permanently.

        The HTTP response status code 301 Moved Permanently is used
        for permanent URL redirection, meaning current links or records
        using the URL that the response is received for should be updated.
        The new URL should be provided in the Location field included with
        the response. The 301 redirect is considered a best practice for
        upgrading users from HTTP to HTTPS.

        Args:
            location (str): Redirect to URL/Location.
        """
        self.status = 301
        self.set_header('Location', location)

    def redirect_found(self, location):
        """ 302 Found.

        The HTTP response status code 302 Found is a common way of
        performing URL redirection.

        An HTTP response with this status code will additionally provide
        a URL in the header field location. The user agent (e.g. a web browser)
        is invited by a response with this code to make a second, otherwise
        identical, request to the new URL specified in the location field.
        The HTTP/1.0 specification (RFC 1945) initially defined this code,
        and gives it the description phrase "Moved Temporarily".

        Many web browsers implemented this code in a manner that violated
        this standard, changing the request type of the new request to GET,
        regardless of the type employed in the original request (e.g. POST).
        For this reason, HTTP/1.1 (RFC 2616) added the new status codes 303
        and 307 to disambiguate between the two behaviours, with 303 mandating
        the change of request type to GET, and 307 preserving the request
        type as originally sent. Despite the greater clarity provided by this
        disambiguation, the 302 code is still employed in web frameworks to
        preserve compatibility with browsers that do not implement the
        HTTP/1.1 specification.

        As a consequence, the update of RFC 2616 changes the definition to
        allow user agents to rewrite POST to GET.

        Args:
            location (str): Redirect to URL/Location.
        """
        self.status = 302
        self.set_header('Location', location)

    def redirect(self, location):
        """ Alias for Redirect See Other
        """
        self.redirect_see_other(location)

    def redirect_see_other(self, location):
        """ 303 See Other.

        The HTTP response status code 303 See Other is a way to redirect web
        applications to a new URI, particularly after a HTTP POST has been
        performed, since RFC 2616 (HTTP 1.1).

        According to RFC 7231, which obsoletes RFC 2616, A 303 response to a
        GET request indicates that the origin server does not have a
        representation of the target resource that can be transferred by the
        server over HTTP. However, the Location field value refers to a
        resoure that is descriptive of the target resource, such that making a
        retrieval request on that other resource might result in a
        representation that is useful to recipients without implying that it
        represents the original target resource.

        This status code should be used with the location header, as described
        below. If a server responds to a POST or other non-idempotent request
        with a 303 See Other response and a value for the location header, the
        client is expected to obtain the resource mentioned in the location
        header using the GET method; to trigger a request to the target
        resource using the same method, the server is expected to provide a 307
        Temporary Redirect response.

        303 See Other has been proposed as one way of responding to a request
        for a URI that identifies a real-world object according to Semantic Web
        theory (the other being the use of hash URIs). For example,
        if http://www.example.com/id/alice identifies a person, Alice, then it
        would be inappropriate for a server to respond to a GET request with
        200 OK , as the server could not deliver Alice herself. Instead the
        server would issue a 303 See Other response which redirected to a
        separate URI providing a description of the person Alice.

        303 See Other can be used for other purposes. For example, when
        building a RESTful web API that needs to return to the caller
        immediately but continue executing asynchronously (such as a long-lived
        image conversion), the web API can provide a status check URI that
        allows the original client who requested the conversion to check on the
        conversion's status. This status check web API should return 303 See
        Other to the caller when the task is complete, along with a URI from
        which to retrieve the result in the Location HTTP header field.

        Args:
            location (str): Redirect to URL/Location.
        """
        self.status = 303
        self.set_header('Location', location)

    def not_modified(self):
        """ 304 Not Modified.

        The 304 (Not Modified) status code indicates that a conditional GET
        or HEAD request has been received and would have resulted in a 200
        (OK) response if it were not for the fact that the condition
        evaluated to false.  In other words, there is no need for the server
        to transfer a representation of the target resource because the
        request indicates that the client, which made the request
        conditional, already has a valid representation; the server is
        therefore redirecting the client to make use of that stored
        representation as if it were the payload of a 200 (OK) response.

        The server generating a 304 response MUST generate any of the
        following header fields that would have been sent in a 200 (OK)
        response to the same request: Cache-Control, Content-Location, Date,
        ETag, Expires, and Vary.

        Since the goal of a 304 response is to minimize information transfer
        when the recipient already has one or more cached representations, a
        sender SHOULD NOT generate representation metadata other than the
        above listed fields unless said metadata exists for the purpose of
        guiding cache updates (e.g., Last-Modified might be useful if the
        response does not have an ETag field).

        Requirements on a cache that receives a 304 response are defined in
        Section 4.3.4 of [RFC7234].  If the conditional request originated
        with an outbound client, such as a user agent with its own cache
        sending a conditional GET to a shared proxy, then the proxy SHOULD
        forward the 304 response to that client.

        A 304 response cannot contain a message-body; it is always terminated
        by the first empty line after the header fields.
        """
        self.status = 304

    def redirect_temporary(self, location):
        """ 307 Temporary Redirect.

        The target resource resides temporarily under a different URI and the
        user agent MUST NOT change the request method if it performs an
        automatic redirection to that URI.

        Since the redirection can change over time, the client ought to
        continue using the original effective request URI for future requests.

        The server SHOULD generate a Location header field in the response
        containing a URI reference for the different URI. The user agent MAY
        use the Location field value for automatic redirection. The server's
        response payload usually contains a short hypertext note with a
        hyperlink to the different URI(s).

        Note: This status code is similar to 302 Found, except that it does not
        allow changing the request method from POST to GET. This specification
        defines no equivalent counterpart for 301 Moved Permanently (RFC7238,
        however proposes defining the status code 308 Permanent Redirect for
        this purpose).

        Args:
            location (str): Redirect to URL/Location.
        """
        self.status = 307
        self.set_header('Location', location)

    def redirect_permanent(self, location):
        """ 308 Permanent Redirect.

        The target resource has been assigned a new permanent URI and any
        future references to this resource ought to use one of the enclosed
        URIs.

        Clients with link editing capabilities ought to automatically re-link
        references to the effective request URI1 to one or more of the new
        references sent by the server, where possible.

        The server SHOULD generate a Location header field in the response
        containing a preferred URI reference for the new permanent URI. The
        user agent MAY use the Location field value for automatic redirection.
        The server's response payload usually contains a short hypertext note
        with a hyperlink to the new URI(s).

        A 308 response is cacheable by default; i.e., unless otherwise
        indicated by the method definition or explicit cache controls.

        Note: This status code is similar to 301 Moved Permanently, except that
        it does not allow changing the request method from POST to GET.

        Args:
            location (str): Redirect to URL/Location.
        """
        self.status = 308
        self.set_header('Location', location)
