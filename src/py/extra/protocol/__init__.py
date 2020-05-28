# TODO: Use Hypercorn, uvicorn
from typing import Any,Optional,Iterable,Any,Tuple,Union,Dict,TypeVar,Generic,List,NamedTuple
from extra.util import Flyweight
from enum import Enum

T = TypeVar('T')

def encode( value:Union[str,bytes] ) -> bytes:
	return bytes(value, "utf8") if isinstance(value,str) else value

class Headers:

	def __init__( self ):
		self._headers:Dict[bytes,List[bytes]] = {}

	def reset( self ):
		self._headers.clear()

	def items( self ) -> Iterable[Tuple[bytes,bytes]]:
		return self._headers.items()

	def get( self, name:str  ) -> Any:
		if name in self._headers:
			count,value = self._headers[name]
			if count == 1:
				return value[0]
			else:
				return value

	def set( self, name:str, value:Any  ) -> Any:
		self._headers[name] = [1, [value]]
		return value

	def add( self, name:str, value:Any  ) -> Any:
		if name not in self._headers:
			return self.set(name, value)
		else:
			v = self._headers[name]
			v[0] += 1
			v[1].append(value)
			return value

class Request(Flyweight):

	# @group Request attributes

	def __init__( self ):
		Flyweight.__init__( self )

	@property
	def uri( self ):
		pass

	# @group Params

	@property
	def params( self ):
		pass

	def getParam( self, name:str  ) -> Any:
		pass

	# @group Loading

	@property
	def isLoaded( self ):
		pass

	@property
	def loadProgress( self ):
		pass

	def load( self  ) -> Any:
		pass

	# @group Files

	@property
	def files( self ):
		pass

	def getFile( self, name:str  ) -> Any:
		pass

	# @group Responses
	def multiple( self ):
		pass

	def redirect( self ):
		pass

	def bounce( self ):
		pass

	def returns( self ):
		pass

	def stream( self ):
		pass

	def local( self ):
		pass

	# @group Errors

	def notFound( self ):
		pass

	def notAuthorized( self ):
		pass

	def notModified( self ):
		pass

	def fail( self ):
		pass

BodyType = Enum("BodyType", "none value iterator")
Body     = NamedTuple("Body", [("type", BodyType), ("content", Union[bytes]), ("contentType", bytes)])

class Response(Flyweight):

	def __init__( self ):
		Flyweight.__init__( self )
		self.status = -1
		self.bodies = []

	def init( self, status:int ):
		self.status = status
		return self

	def reset( self ):
		self.bodies.clear()

	def setCookie( self, name:str, value:Any ):
		pass

	def setHeader( self, name:str, value:Any ):
		pass

	def setContent( self, content:Union[str,bytes], contentType:Optional[Union[str,bytes]]=None) -> 'Response':
		if isinstance(content, str):
			# SEE: https://www.w3.org/International/articles/http-charset/index
			self.bodies.append((encode(content), b"text/plain; charset=utf-8"))
		elif isinstance(content, bytes):
			self.bodies.append((content, encode(contentType or b"application/binary")))
		else:
			raise ValueError(f"Content type not supported, choose 'str' or 'bytes': {content}")
		return self

	def read( self ) -> Iterable[Union[bytes,None]]:
		yield None
		pass

# EOF